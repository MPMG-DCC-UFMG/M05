from mpmg.services.elastic import Elastic
from mpmg.services.models import Processo, Diario, DiarioSegmentado, Licitacao
from mpmg.services.models.api_config import APIConfig
from .config_learning_to_rank import ConfigLearningToRank

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

    def __init__(self):
        self.elastic = Elastic()

        self.ltr_config = ConfigLearningToRank().get(1)
        print(self.ltr_config)
        self.retrievable_fields = APIConfig.retrievable_fields()
        self.highlight_field = APIConfig.highlight_field()

        # relaciona o nome do índice com a classe Django que o representa
        self.index_to_class = APIConfig.searchable_index_to_class()

    def search(self, indices, query, must_queries, should_queries, filter_queries, page_number, results_per_page):
        start = results_per_page * (page_number - 1)
        end = start + results_per_page

        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=indices) \
            .source(self.retrievable_fields) \
            .query("bool", must=must_queries, should=should_queries, filter=filter_queries)[start:end] \
            .highlight(self.highlight_field, fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False, type="unified")

        if self.ltr_config["ativo"]:
            elastic_request.extra(rescore={"window_size": self.ltr_config["quantidade"],
                                            "query": {"rescore_query": {"sltr": {
                                                "params": {"consulta": f"{query}"},
                                                "model": self.ltr_config["modelo"]
                                }}}})

        response = elastic_request.execute()
        total_docs = response.hits.total.value
        # Total retrieved documents per page + 1 page for rest of division
        total_pages = (total_docs // results_per_page) + 1
        documents = []

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

        return total_docs, total_pages, documents, response.took
