from urllib import response
from elasticsearch import Elasticsearch
import elasticsearch_dsl

if __name__ == '__main__':
    es = Elasticsearch(hosts=['http://localhost:9200'])
    dsl = elasticsearch_dsl

    doc = es.get(index='consumidor_gov', id='887294ae05f12316032481eae6594bee')
    print(doc)