from collections import defaultdict

class FeaturesExtractor:
    '''
    Parseia o "explain" do elasticsearch para extrair features.
    Numa pesquisa por "belo horizonte" em documentos com os campos "conteudo" e "titulo",
    produzirá a seguinte estrutura:

        DOC_ID:{
            conteudo:{
                field_length:0, 
                avg_field_length:0,
                matched_terms:{
                    termo1:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                    termo2:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                }
            },
            titulo:{
                field_length:0, 
                avg_field_length:0,
                matched_terms:{
                    termo1:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                }
            }
        }
    
    field_length: número de tokens daquele campo naquele documento
    avg_field_length: tamanho médio desse campo em todo o índice
    tf: frequeência do termo naquele campo para aquele documento
    idf: inverso da frequência do termo para aquele campo naquele documento
    num_docs_term: número de documentos que contém o termo em questão.
    total_docs: número de documentos que possui o campo em questão
    '''
    #TODO: Nessa estrutura, o q acontece com documentos com mesmo id so que de indices difetentes?

    def __init__(self, fields):
        self.features = {}
        self.fields = fields
    

    def extract(self, elastic_response):
        for hit in elastic_response:
            # print(hit.meta.id)
            self.features[hit.meta.id] = {}
            for field in self.fields:
                self.features[hit.meta.id][field] = {'matched_terms':defaultdict(dict), 'field_length':0, 'avg_field_length':0}
            
            self._parse_node(hit.meta.id, None, None, hit.meta.explanation, '')
        
        # print(self.features)
        return self.features
    

    def _parse_node(self, doc_id, current_field, current_term, json_node, space):
        # qual campo e qual termo
        if json_node['description'].startswith('weight'):
            current_field = json_node['description'][7:json_node['description'].index(':')]
            current_term = json_node['description'][json_node['description'].index(':')+1:json_node['description'].index(' ')]
            # print(current_field, current_term)
        
        elif json_node['description'].startswith('idf,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['idf'] = json_node['value']
        
        elif json_node['description'].startswith('n,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['num_docs_term'] = json_node['value']
        
        elif json_node['description'].startswith('N,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['total_docs'] = json_node['value']
        
        elif json_node['description'].startswith('tf,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['tf'] = json_node['value']
        
        elif json_node['description'].startswith('dl,'):
            self.features[doc_id][current_field]['field_length'] = json_node['value']
        
        elif json_node['description'].startswith('avgdl,'):
            self.features[doc_id][current_field]['avg_field_length'] = json_node['value']
        
        # print(space, json_node['value'], json_node['description'])
        if len(json_node['details']) > 0:
            for item in json_node['details']:
                self._parse_node(doc_id, current_field, current_term, item, space+'    ')


from .elastic import Elastic
import math
# import json

class TermVectorsFeaturesExtractor:
    '''
    {   
        DOC_ID:{
            conteudo:{
                field_length:0, 
                avg_field_length:0,
                matched_terms:{
                    termo1:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                    termo2:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                }
            },
            titulo:{
                field_length:0, 
                avg_field_length:0,
                matched_terms:{
                    termo1:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                }
            }
        },
        ...
    }   
    field_length: número de tokens daquele campo naquele documento
    avg_field_length: tamanho médio desse campo em todo o índice
    tf: frequeência do termo naquele campo para aquele documento
    idf: inverso da frequência do termo para aquele campo naquele documento
    num_docs_term: número de documentos que contém o termo em questão.
    total_docs: número de documentos que possui o campo em questão
    '''

    def __init__(self, fields, query_terms, indices):
        self.features = {}
        self.fields = fields
        self.indices = indices
        self.query_terms = query_terms
    
    def extract(self, elastic_response):
        term_vectors = self._get_term_vectors(elastic_response)
        
        for doc in term_vectors['docs']:
            self.features[doc['_id']] = {}
            for field in self.fields:

                matched_terms = {}
                for term in doc['term_vectors'][field]['terms']:
                    matched_terms[term] = {
                        'tf': doc['term_vectors'][field]['terms'][term]['term_freq'],
                        'idf': self._idf(doc['term_vectors'][field]['terms'][term]),
                        'num_docs_term': doc['term_vectors'][field]['terms'][term]["doc_freq"], #number of documents containg the term
                        'total_docs': int(Elastic().es.cat.count(index = self.indices).replace("\n", "").split(" ")[-1]) #numbers of documents in the colection
                    }
                
                self.features[doc['_id']][field] = {
                    "field_length": 0, 
                    "avg_field_length": 0,
                    "matched_terms": matched_terms
                }
                
        # print(json.dumps(self.features, indent="  "))
        return self.features
        
    
    def _idf(self, term):
        N = int(Elastic().es.cat.count(index = self.indices).replace("\n", "").split(" ")[-1]) #numbers of documents in the colection
        n = term["doc_freq"] #number of documents containg the term
        idf = math.log2( (N)/(n+1))
        # idf = math.log2( (N - n + 0.5)/(n + 0.5) )        
        # print("N: {}\nn: {}\nidf:{}".format(N, n, idf))
        return idf


    def _get_term_vectors(self, elastic_response):
        '''
        Formato:
        {
            'docs': [
                {
                    '_index': 'diarios_teste',
                    '_id': 'XSbT3HIB5C7V0GBitYVg',
                    'term_vectors': {
                        'conteudo': {
                            'terms': {
                                'luiz': {
                                    'doc_freq': 3081,
                                    'ttf': 36755,
                                    'term_freq': 370
                                }
                            }
                        },
                        'titulo': {
                            'terms': {}
                        }
                    }
                },
                {
                    '_index': 'diarios_teste',
                    '_id': 'WCbT3HIB5C7V0GBi6ohd',
                    'term_vectors': {
                        'conteudo': {
                            'terms': {
                                'luiz': {
                                    'doc_freq': 3081,
                                    'ttf': 36755,
                                    'term_freq': 289
                                }
                            }
                        },
                        'titulo': {
                            'terms': {}
                        }
                    }
                }
            ]
        }

        '''
        docs = [
            {
                "_index": hit["_index"],
                "_id": hit["_id"],
                "term_statistics": True,
                "offsets": False,
                "payloads": False,
                "positions": False,
                "fields": self.fields
            } for hit in elastic_response['hits']['hits']
        ]
        
        response = Elastic().es.mtermvectors(body = { "docs": docs })
        filtred_term_vectors = {"docs":[]}
        for doc in response["docs"]:
            
            doc_term_vectors = {}
            for field in self.fields:
                doc_term_vectors[field] = { 'terms': {} }
                for term in self.query_terms:
                    if term in doc["term_vectors"][field]['terms']:
                        doc_term_vectors[field]['terms'][term] = doc["term_vectors"][field]['terms'][term] 

            filtred_term_vectors["docs"].append({
                "_index": doc["_index"],
                "_id": doc["_id"],
                "term_vectors": doc_term_vectors
            })
            
        return filtred_term_vectors
        