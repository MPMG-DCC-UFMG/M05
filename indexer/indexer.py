import csv
import ctypes
import os
import time
import json
from copy import deepcopy
from random import random
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


def parse_date(text):
    for fmt in ('%Y-%m-%d', "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

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

    def generate_formated_csv_lines(self, file_path, index, encoding="utf8"):
        """
        Generates formated entries to indexed by the bulk API
        """
        file = open(file_path, encoding=encoding)
        table = csv.DictReader(file)

        file_count = open(file_path, encoding=encoding)
        table_count = csv.DictReader(file_count)

        sentences_num = 0

        columns = table.fieldnames.copy()

        rows = list(table_count)
        lines_num = len(rows)
        for line in tqdm(table, total=lines_num):
            line = dict(line)
            doc = {}
            for field in columns:
                if line[field] == '':
                    continue

                field_name = field
                field_type = None
                if len(field.split(":")) > 1:
                    field_name = field.split(":")[0]
                    field_type = field.split(":")[-1]

                if field_type == "list":
                    doc[field_name] = eval(line[field])
                elif field_name == 'data':
                    if line[field] != '':
                        element = parse_date(line[field])
                        timestamp = datetime.datetime.timestamp(element)
                        doc[field_name] = timestamp
                else:
                    doc[field_name] = line[field]

            if self.model_path != "None":
                doc["embedding_vector"] = change_vector_precision(get_dense_vector(self.sentence_model, line['conteudo']))

            yield {
                "_index": index,
                "_source": doc
            }
        
        print("Sentences mean: ", sentences_num/lines_num)

    def simple_indexer(self, files_to_index, index):
        """
        Index the csvs files using helpers.bulk
        """
        start = time.time()

        responses = {}
        for csv_file in files_to_index:
            print("Indexing: " + csv_file)
            responses[csv_file] =  helpers.bulk(self.es, self.generate_formated_csv_lines(csv_file, index) )
            print("  Response: " + str(responses[csv_file]))

            if len(responses[csv_file][1]) > 0 :
                print("Detected error while indexing: " + csv_file)
            else:
                end = time.time()
                print("Indexing time: {:.4f} seconds.".format(end-start))

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
            except:
                error = True
                print("Detected error while indexing: " + csv_file)

        if not error:
            print("All files indexed with no error.")
            end = time.time()
            print("Indexing time: {:.4f} seconds.".format(end-start))
        else:
            print("Error while indexing.")

