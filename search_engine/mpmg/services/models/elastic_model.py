from elasticsearch.exceptions import NotFoundError

from mpmg.services.elastic import Elastic

class ElasticModel(dict):
    '''
    Classe abstrata que representa um índice no elasticsearch.
    Cada índice do elasticsearch deve ter uma classe correspondente 
    que herda dessa.

    Exemplo:

    class MeuIndice(ElasticModel):
        index_name = 'meu_indice'

        def __init__(self, **kwargs):
            index_name = MeuIndice.index_name
            meta_fields = ['_id']
            index_fields = ['campo_um', 'campo_dois']
            super().__init__(index_name, meta_fields, index_fields, **kwargs)


    Nota: Esta classe herda de dict para que o django consiga serializa-la em
    json automaticamente.
    '''

    # atributos estáticos necessários para os métodos estáticos abaixo
    elastic = Elastic()
    index_name = None
    results_per_page = 10

    def __init__(self, index_name, meta_fields, index_fields, **kwargs):
        self.elastic = ElasticModel.elastic
        self.index_name = index_name
        self.meta_fields = meta_fields
        self.index_fields = index_fields
        self.allowed_attributes = self.meta_fields + self.index_fields

        for field in self.meta_fields:
            setattr(self, field, kwargs.get(field, None))

        for field in self.index_fields:
            setattr(self, field, kwargs.get(field, None))

        # passa pro dict apenas os allowed_attributes
        serializable_attributes = {}
        for k, v in self.__dict__.items():
            if k in self.allowed_attributes:
                serializable_attributes[k] = v
        super().__init__(serializable_attributes)

    def set_attributes(self, dict_data):
        '''
        Seta os atributos do objeto no formato de dict, onde a chave representa o atributo.
        As chaves do dict_data devem coincidir com as que foram especificadas em index_fields
        e meta_fields
        '''
        for field, value in dict_data.items():
            if field in self.allowed_attributes:
                setattr(self, field, value)

    def parse_dict_data(self, dict_data: dict = None) -> dict:
        '''
        Proprocessamento de dict_data.

        Chaves passadas em dict_data que não estiverem especificadas em index_fields serão ignoradas.
        Se dict_data for igual a None, os atributos do objeto é que serão salvos.
        '''
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')
        return dict_data

    def save(self, dict_data=None):
        '''
        Salva o objeto no índice. Os valores a serem salvos podem ser passados em dict_data.
        '''
        dict_data = self.parse_dict_data(dict_data)

        response = self.elastic.es.index(index=self.index_name, body=dict_data)
        if response['result'] != 'created':
            return None

        return response['_id']

    def delete(self, item_id: str) -> bool:
        try:
            response = self.elastic.es.delete(
                index=self.index_name, id=item_id)
            return response['result'] == 'deleted'

        except:
            return False

    @classmethod
    def get(cls, item_id):
        '''
        Busca um elemento no índice diretamente pelo seu ID.
        Retorna uma instância da classe correspondente ao índice em questão.
        '''
        try:
            retrieved_element = cls.elastic.dsl.Document.get(
                item_id, using=cls.elastic.es, index=cls.index_name)
            element = {'id': retrieved_element.meta.id,
                       **retrieved_element.to_dict()}
            return cls(**element)

        except NotFoundError:
            return None

    @classmethod
    def get_total(cls):
        '''
        Retorna o total de registros salvos no índice.
        '''
        total = cls.elastic.dsl.Search(
            using=cls.elastic.es, index=cls.index_name).count()
        return total

    @classmethod
    def get_list(cls, query=None, page=1, sort=None):
        '''
        Busca uma lista de documentos do índice. Cada item da lista é uma instância da classe
        em questão. É possível passar parâmetros de ordenação em sort, e também parâmetros de 
        consulta em query. 
        O tamanho da lista será de acordo com o atributo results_per_page da classe e os dados
        retornados serão de acordo com a página definida pelo parâmetro page.
        Caso queira retornar todos os registros, sem fazer paginação, passe page='all'
        Exemplo:

        query_param = {"bool":{"must":{"term":{"text_consulta":"glater"}}}}
        sort_param = {'data_criacao':{'order':'desc'}}
        LogSearch.results_per_page = 20
        LogSearch.getList(query=query_param, page=3, sort=sort_param)
        '''

        search_obj = cls.elastic.dsl.Search(
            using=cls.elastic.es, index=cls.index_name)

        if query != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q(query))

        if page == 'all':
            total = cls.get_total()
            search_obj = search_obj[0:total]
        else:
            start = cls.results_per_page * (page - 1)
            end = start + cls.results_per_page
            search_obj = search_obj[start:end]

        if sort != None:
            search_obj = search_obj.sort(sort)

        elastic_result = search_obj.execute()

        total_records = elastic_result.hits.total.value

        result_list = []

        for item in elastic_result:
            result_list.append(
                cls(**dict({'id': item.meta.id}, **item.to_dict())))

        return total_records, result_list

    @staticmethod
    def get_indices_info():
        info = []
        response = ElasticModel.elastic.es.cat.indices()
        parts = response.strip().split('\n')

        for part in parts:
            try:
                subpart = part.strip().split()

                if subpart[2][0] == '.':
                    continue

                info.append({
                    'health': subpart[0],
                    'status': subpart[1],
                    'index_name': subpart[2],
                    'uuid': subpart[3],
                    'num_primary_shards': subpart[4],
                    'num_replica_shards': subpart[5],
                    'num_documents': subpart[6],
                    'num_deleted_docs': subpart[7],
                    'total_store_size': subpart[8],
                    'primary_store_size': subpart[9]
                })

            except:
                pass

        info = sorted(info, key=lambda item: item['index_name'])
        return info

    @staticmethod
    def get_cluster_info():
        response = ElasticModel.elastic.es.cluster.stats()
        return response
