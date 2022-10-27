import csv
import ctypes
import time
import datetime

import nltk
from tqdm import tqdm
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from sentence_transformers import SentenceTransformer, models
from torch import nn
import numpy as np
from nltk import tokenize
nltk.download('punkt')

from os import listdir
from os.path import isfile, join
import gzip


def list_files(path):
    """
    List all files from a given folder
    """
    if path[-1] != "/":
        path = path+"/"
    return [path+f for f in listdir(path) if isfile(join(path, f))]


def get_sentences(text):
    tokens = text.replace("\n", "").replace("\r", "").split()
    text = " ".join(tokens)
    return tokenize.sent_tokenize(text)


def get_dense_vector(model, text_list):
    vectors = model.encode([text_list])
    vectors = [vec.tolist() for vec in vectors]
    return vectors[0]


def get_sentence_model(model_path="neuralmind/bert-base-portuguese-cased"):
    word_embedding_model = models.Transformer(model_path, max_seq_length=500)
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())

    return SentenceTransformer(modules=[word_embedding_model, pooling_model])


def change_vector_precision(vector, precision=24):
    vector = np.array(vector, dtype=np.float16)
    return vector.tolist()

def parse_date(text):
    for fmt in ('%Y-%m-%d', "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def get_current_timestamp_in_ms() -> float:
    return round(time.time() * 1000)

class Indexer:

    def __init__(self, elastic_address='localhost:9200', model_path="neuralmind/bert-base-portuguese-cased", username=None, password=None):

        self.ELASTIC_ADDRESS = elastic_address

        if username != None and password != None:
            self.es = Elasticsearch([self.ELASTIC_ADDRESS], timeout=120, max_retries=3, retry_on_timeout=True, http_auth=(username, password))
        else:
            self.es = Elasticsearch([self.ELASTIC_ADDRESS], timeout=120, max_retries=3, retry_on_timeout=True)
        
        self.model_path = model_path
        if self.model_path != "None":
            self.sentence_model = get_sentence_model(self.model_path)

        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

    def generate_formated_csv_lines(self, file_path, index, encoding="utf-8"):
        """
        Generates formated entries to indexed by the bulk API
        """

        mapping = self.es.indices.get_mapping(index=index)[index]['mappings']['properties']

        if file_path[-3:] == '.gz':
            csv_file = gzip.open(file_path, 'rt', encoding=encoding)
            file_count = gzip.open(file_path, 'rt', encoding=encoding)
        else:
            csv_file = open(file_path, encoding=encoding)
            file_count = open(file_path, encoding=encoding)
        
        table = csv.DictReader(csv_file)
        table_count = csv.DictReader(file_count)

        sentences_num = 0

        columns = table.fieldnames.copy()

        rows = list(table_count)
        lines_num = len(rows)
        for line in tqdm(table, total=lines_num):
            line = dict(line)
            doc = {}
            for field in columns:
                if field == 'id': # id vai separado, fora do doc
                    continue

                field_name = field
                field_type = None
                if len(field.split(":")) > 1:
                    field_name = field.split(":")[0]
                    field_type = field.split(":")[-1]

                if field_type == "list":
                    doc[field_name] = eval(line[field])
                
                elif field_type == "bool":
                    doc[field_name] = eval(line[field])

                elif field_name == 'data_criacao':
                    if line[field] != '':
                        element = parse_date(line[field])
                        timestamp = datetime.datetime.timestamp(element)
                        doc[field_name] = timestamp

                elif field_name == 'categoria_empresa':
                    categories = eval(line[field]) if line[field] != '' else []
                    doc[field_name] = categories

                # elif field_name == 'data_indexacao':
                #     if line[field] != '':
                #         element = parse_date(line[field])
                #         timestamp = datetime.datetime.timestamp(element)
                #         doc[field_name] = timestamp

                else:
                    doc[field_name] = line[field]

            field_name = 'data_indexacao'

            if field_name in mapping:
                if bool(line.get(field_name)):
                    element = parse_date(line[field_name])
                    timestamp = datetime.datetime.timestamp(element)
                    doc[field_name] = timestamp
                else:                    
                    doc[field_name] = get_current_timestamp_in_ms()

            if self.model_path != "None" and 'conteudo' in line:
                doc["embedding"] = change_vector_precision(get_dense_vector(self.sentence_model, line['conteudo']))
            
            return_item = {
                "_index": index,
                "_source": doc
            }

            if "id" in columns:
                return_item['_id'] = line['id']

            yield return_item
        
        csv_file.close()
        file_count.close()
        print("Sentences mean: ", sentences_num/lines_num)

    def simple_indexer(self, files_to_index, index):
        """
        Index the csvs files using helpers.bulk
        """
        start = time.time()

        responses = {}
        for csv_file in files_to_index:
            try:
                print("Indexing: " + csv_file)
                responses[csv_file] =  helpers.bulk(self.es, self.generate_formated_csv_lines(csv_file, index) )
                print("  Response: " + str(responses[csv_file]))

                if len(responses[csv_file][1]) > 0 :
                    # print("Detected error while indexing: " + csv_file)
                    print(responses[csv_file])
                else:
                    end = time.time()
                    print("Indexing time: {:.4f} seconds.".format(end-start))
            except Exception as e:
                print(e)

    def parallel_indexer(self, files_to_index, index, thread_count):
        """
        Index the csvs files using helpers.parallel_bulk
        Note that the queue_size is the same as thread_count
        """
        start = time.time()

        error = False
        for csv_file in files_to_index:
            try:
                print("Indexing: " + csv_file + "...")
                for success, info in helpers.parallel_bulk(self.es, self.generate_formated_csv_lines(csv_file, index), thread_count = thread_count, queue_size = thread_count): 
                    if not success:
                        print("Detected error while indexing: " + csv_file)
                        error = True
                        print(info)
            except Exception as e:
                error = True
                # print(e)
                print("Detected error while indexing: " + csv_file)

        if not error:
            print("All files indexed with no error.")
            end = time.time()
            print("Indexing time: {:.4f} seconds.".format(end-start))
        else:
            print("Error while indexing.")

