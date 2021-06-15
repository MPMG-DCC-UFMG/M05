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
    vectors = model.encode(text_list)
    vectors = [vec.tolist() for vec in vectors]
    return vectors


def get_sentence_model(model_path="neuralmind/bert-base-portuguese-cased"):
    word_embedding_model = models.Transformer(model_path, max_seq_length=500)
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())

    return SentenceTransformer(modules=[word_embedding_model, pooling_model])


class Indexer:

    def __init__(self, elastic_address='localhost:9200', model_path="neuralmind/bert-base-portuguese-cased"):

        self.ELASTIC_ADDRESS = elastic_address
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
                        element = datetime.datetime.strptime(line[field],"%d-%m-%Y")
                        timestamp = datetime.datetime.timestamp(element)
                        doc[field_name] = timestamp
                else:
                    doc[field_name] = line[field]

            if self.model_path != "None":
                sentences = get_sentences(line['conteudo'])
                doc["sentences_vectors"] = [{"vector": vector} for vector in get_dense_vector(self.sentence_model, sentences)]

            yield {
                "_index": index,
                "_source": doc
            }

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

