from dataclasses import fields
from urllib import response
from mpmg.services.elastic import Elastic
from mpmg.services.models.api_config import APIConfig

from elasticsearch_dsl import A
from elasticsearch_dsl.query import MoreLikeThis

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

    def search_similar(self, indices, doc_type, doc_id):
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=indices) \
                            .query(MoreLikeThis(like=[{
                                '_index': doc_type,
                                '_id': doc_id,
                            }], fields=['titulo', 'conteudo']))
        
        response = elastic_request.execute()
        total_docs = response.hits.total.value

        documents = []
        for item in response:
            dict_data = item.to_dict()

            dict_data['id'] = item.meta.id

            dict_data['tipo'] = item.meta.index

            result_class = self.index_to_class[item.meta.index]

            documents.append(result_class(**dict_data))
        
        return documents

    def search(self, indices, must_queries, should_queries, filter_queries, page_number, results_per_page, sort_by='relevancia', sort_order='desc'):
        agg = A('terms', field='_index')

        start = results_per_page * (page_number - 1)
        end = start + results_per_page

        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=indices) \
            .extra(track_total_hits=True) \
            .source(self.retrievable_fields) \
            .query("bool", must=must_queries, should=should_queries, filter=filter_queries)[start:end] \
            .highlight(self.highlight_field, fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False, type="unified")

        if sort_by == 'data':
            elastic_request = elastic_request.sort({'data_criacao': {'order': sort_order}})

        elastic_request.aggs.bucket('per_index', agg)

        response = elastic_request.execute()
        total_docs = response.hits.total.value
        # Total retrieved documents per page + 1 page for rest of division
        total_pages = (total_docs // results_per_page) + 1
        documents = []

        try:
            buckets = response.aggregations['per_index']['buckets']
        
        except:
            buckets = []

        doc_counts_by_index = {index: 0 for index in indices}
        for bucket in buckets:
            index = bucket['key']
            doc_count = bucket['doc_count']
            doc_counts_by_index[index] = doc_count

        for i, item in enumerate(response):
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id

            if hasattr(item.meta, 'highlight'):
                dict_data['descricao'] = item.meta.highlight.conteudo[0]

            else:
                dict_data['descricao'] = 'Sem descrição.'

            dict_data['posicao_ranking'] = results_per_page * \
                (page_number-1) + (i+1)

            dict_data['tipo'] = item.meta.index

            result_class = self.index_to_class[item.meta.index]

            documents.append(result_class(**dict_data))
  
        return total_docs, total_pages, documents, response.took, doc_counts_by_index