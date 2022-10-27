import json
from mpmg.services.elastic import Elastic
from mpmg.services.models.api_config import APIConfig

from elasticsearch_dsl import A

class Document:
    '''
    Classe que abstrai as diferentes classes (índices) que podem ser
    pesquisadas pela busca.
    Essa classe é responsável por buscar em diferentes índices e retornar
    uma lista de resultados com diferentes instâncias de classes.

    Diferente das demais, esta classe não herda de ElasticModel justamente
    por não representar um único índice, mas sim um conjunto de diferentes
    índices (classes). Ela fica responsável apenas por realizar a busca e 
    retornar os resultados como uma lista de múltiplas classes.
    '''

    def __init__(self, api_client_name):
        self.elastic = Elastic()
        self.api_client_name = api_client_name
        self.retrievable_fields = APIConfig.retrievable_fields(api_client_name)
        self.highlight_field = APIConfig.highlight_field(api_client_name)
        
        # relaciona o nome do índice com a classe Django que o representa
        self.index_to_class = APIConfig.searchable_index_to_class(api_client_name)

    def search(self, indices, match_query, knn_query, aggs):
        response = self.elastic.es.search(index=indices, query=match_query, knn=knn_query, aggs=aggs, source=self.retrievable_fields)
        doc_counts_by_index = {index: 0 for index in indices}

        buckets = response['aggregations']['per_index']['buckets']
        for bucket in buckets:
            doc_counts_by_index[bucket['key']] = bucket['doc_count']

        documents = []

        hits = response['hits']['hits']
        total_docs = len(hits)

        for i, item in enumerate(hits):
                dict_data = item['_source']
                dict_data['id'] = item['_id']

                dict_data['descricao'] = dict_data['conteudo'][:500]

                dict_data['posicao_ranking'] = i

                dict_data['tipo'] = item['_index']

                result_class = self.index_to_class[item['_index']]

                documents.append(result_class(**dict_data))
 

        return total_docs, 1, documents, response['took'], doc_counts_by_index
