from itertools import count
from typing import Tuple, Union
from elasticsearch.exceptions import NotFoundError

from mpmg.services.elastic import Elastic
from mpmg.services.utils import get_current_timestamp
from mpmg.services.utils import str2bool

# TODO: aumentar cobertura
ELASTIC_TYPE_TO_PYTHON_TYPE = {
    'text': str,
    'boolean': str2bool,
    'integer': int,
    'number': float,
    'float': float 
}

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
        
        fields = list(dict_data.keys())
        for field in fields:
            if field not in self.index_fields:
                del dict_data[field]

        return dict_data

    def save(self, dict_data=None, item_id: str = None) -> Union[str, None]:
        '''
        Salva o objeto no índice. Os valores a serem salvos podem ser passados em dict_data.
        '''
        dict_data = self.parse_dict_data(dict_data)
        
        now = get_current_timestamp()

        # Se o objeto a ser salvo possui o campo data_criacao, editamos ele para ter o valor corrente
        if 'data_criacao' in self.index_fields:
            dict_data['data_criacao'] = now 

        # Se o objeto a ser salvo possui o campo data_modificacao, editamos ele para ter o valor corrente
        if 'data_modificacao' in self.index_fields:
            dict_data['data_modificacao'] = now

        if item_id is None:
            response = self.elastic.es.index(index=self.index_name, body=dict_data)
        
        else:
            response = self.elastic.es.index(index=self.index_name, id=item_id, body=dict_data)

        if response['result'] != 'created':
            return None

        return response['_id']

    def delete(self, item_id: str) -> bool:
        '''Deleta o documento item_id do índice.
        '''
        try:
            response = self.elastic.es.delete(
                index=self.index_name, id=item_id)
            return response['result'] == 'deleted'

        except:
            return False

    def update(self, item_id: str, updated_fields: dict) -> bool:
        '''Método responsável por atualizar os campos de um documento.
        '''
        try:
            # Se o objeto a ser salvo possui o campo data_modificacao, editamos ele para ter o valor corrente
            if 'data_modificacao' in self.index_fields:
                updated_fields['data_modificacao'] = get_current_timestamp()

            response = self.elastic.es.update(index=self.index_name, 
                        id=item_id, body={"doc": updated_fields})
            return response['result'] == 'updated' 
        
        except:
            return False 

    @classmethod
    def mapping(cls) -> dict:
        index_mapping = dict()
        raw_mapping = cls.elastic.es.indices.get_mapping(index=cls.index_name)[cls.index_name]
        raw_mapping = raw_mapping['mappings']['properties'] 
        for prop in raw_mapping:
            index_mapping[prop] = raw_mapping[prop]['type']
        return index_mapping

    @classmethod
    def parse_data_type(cls, data: dict, extra_fields: dict = None):
        index_mapping = cls.mapping()
        if extra_fields is not None:
            index_mapping.update(extra_fields)

        for field, value in data.items():
            field_es_type = index_mapping[field]
            data[field] = ELASTIC_TYPE_TO_PYTHON_TYPE[field_es_type](value)

    @classmethod
    def get(cls, item_id):
        '''
        Busca um elemento no índice diretamente pelo seu ID.
        Retorna uma instância da classe correspondente ao índice em questão.
        '''
        try:
            retrieved_element = cls.elastic.es.get(index=cls.index_name, id=item_id)
            source = retrieved_element['_source']
            element = {'id': retrieved_element['_id'], **source}
            return cls(**element)

        except NotFoundError:
            return None

    @classmethod
    def get_total(cls):
        '''
        Retorna o total de registros salvos no índice.
        '''
        response = cls.elastic.es.count(index=cls.index_name)
        return response['count']

    @classmethod
    def item_already_updated(cls, ref: dict, item: dict) -> bool:
        # se ao menos um campo a ser atualizado é diferente do atual 
        for field, value in item.items():
            if ref[field] != value:
                return False
        return True

    @classmethod
    def get_list(cls, query=None, filter=[], page=1, sort=None) -> Tuple[int, list]:
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

        query_param = {'bool': {'must': []}}
        if query != None:
            query_param['bool']['must'].append(query)
        
        if len(filter) > 0:
            for f in filter:
                query_param['bool']['must'].append(f)
        else:
            query_param = query 

        if type(query_param) is dict:
            if len(query_param['bool']['must']) == 0:
                query_param = None
        
        if page == 'all':
            start = None
            end = cls.get_total()

        else:
            start = cls.results_per_page * (page - 1)
            end = None 

        response = cls.elastic.es.search(index=cls.index_name, query=query_param, sort=sort, from_=start, size=end)

        total_records = response['hits']['total']['value'] 
        hits = response['hits']['hits']

        result_list = []

        for hit in hits:
            item_id = hit['_id']
            item = hit['_source']
            result_list.append(
                cls(**dict({'id': item_id}, **item)))

        return total_records, result_list

    @staticmethod
    def get_indices_info(searchable_indices: set):
        info = []
        response = ElasticModel.elastic.es.cat.indices()

        parts = response.strip().split('\n')

        for part in parts:
            try:
                subpart = part.strip().split()

                if subpart[2][0] == '.':
                    continue
                
                if subpart[2] not in searchable_indices:
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
