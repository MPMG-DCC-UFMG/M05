"""
Imports
"""
import numpy as np
import pandas as pd
import csv
import chardet
import ctypes
import os
import argparse

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from os import listdir
from os.path import isfile, join


""" 
Configs
"""
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))


"""
Functions
"""
def list_files(mypath):
    if mypath[-1] != "/":
        mypath = mypath+"/"
    return [mypath+f for f in listdir(mypath) if isfile(join(mypath, f))]


def generate_formated_csv_lines(file_path, index_name, doc_type, encoding="utf8"):
    file = open(file_path, encoding=encoding)
    table = csv.DictReader(file)
    columns = table.fieldnames.copy()
    
    for line in table:
        line = dict(line)
        doc = {}
        for field in columns:
            doc[field] = line[field]
        
        doc["fonte_csv"] = file_path
    
        yield {
            "_index": index_name,
            "_type": doc_type,
            "_source": doc
        }


"""
Script
"""
# Define the args that thae program will accept
parser = argparse.ArgumentParser(description='Indexa arquivos csv no ES dado.')

parser.add_argument("-index", help="Index", required=True)
parser.add_argument("-doctype", help="Type of the indexing documets", required=True)
parser.add_argument("-f", nargs='+', help="List of csv files to index")
parser.add_argument("-d", nargs='+', help="List of directories which all files will be indexed")

# Get all args
args = vars(parser.parse_args())


# Generates the list with all files to index
files_to_index = []

if args['f'] != None:
    for f in args['f']:
        if isfile(f):
            files_to_index.append(f)

for folder in args['d']:
    for f in list_files(folder):
        files_to_index.append(f)


# Creating ES conection
es = Elasticsearch(timeout=30, max_retries=3, retry_on_timeout=True)


# Index all the csv files in the list
responses = {}
for csv_file in files_to_index:
    print("Indexing: " + csv_file)
    responses[csv_file] =  helpers.bulk(es, generate_formated_csv_lines(csv_file, args['index'], args["doctype"]) ) 
    print("Response: " + str(responses[csv_file]))

    if len(responses[csv_file][1]) > 0 :
        print("Detected error while indexing " + csv_file)

