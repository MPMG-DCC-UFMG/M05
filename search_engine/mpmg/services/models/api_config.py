from mpmg.services.elastic import Elastic
from mpmg.services.models import Processo, Diario, DiarioSegmentado, Licitacao

class APIConfig():
    '''
    Classe responsável por controlar todas as configurações da API.
    As confiogurações estão armazenadas em diferentes índices no elasticsearch
    sob o prefixo "config_". Porém, esta classe abstrai essas divisões, concentrando
    tudo numa única classe.

    A título de documentação, segue a relação de índices que armazenam as configurações:

    - config_indices: 
      Armazena o nome dos índices que podem ser buscados, se estão ativos e qual o nome
      da classe python que o representa.
    
    - config_fields:
      Armazena a relação de campos dos documentos, se eles devem ser considerados na busca
      e qual seu peso nela.
    
    - config_options:
      Armazena opções da API que consistem em valores individuais. Por exemplo, número de
      resultados por página, nome do campo que deve ser feito o highlight de busca, etc
    
    - config_entities_mapping
      Mapeia o tipo da entidade do módulo NER para o respectivo campo nos índices

    '''
    
    elastic = Elastic()
    INDEX_CONFIG_INDICES = 'config_indices'
    INDEX_CONFIG_FIELDS = 'config_fields'
    INDEX_CONFIG_OPTIONS = 'config_options'
    INDEX_CONFIG_ENTITIES = 'config_entities_mapping'

    def __init__(self, **kwargs):
        None


    # CONFIGURAÇÕES DAS OPÇÕES ######################################################################

    @classmethod
    def use_semantic_vectors_in_search(cls):
        return cls.get_options()['use_semantic_vectors_in_search']
    
    @classmethod
    def identify_entities_in_query(cls):
        return cls.get_options()['identify_entities_in_query']
    
    @classmethod
    def highlight_field(cls):
        return cls.get_options()['highlight_field']
    
    @classmethod
    def results_per_page(cls):
        return cls.get_options()['results_per_page']


    @classmethod
    def get_options(cls):
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_OPTIONS)
        elastic_result = search_obj.execute()
        item = elastic_result[0]
        options = dict({'id': item.meta.id}, **item.to_dict())
        return options
    
    
    # CONFIGURAÇÕES DOS CAMPOS ######################################################################
    
    @classmethod
    def searchable_fields(cls):
        '''
        Retorna uma lista com o nome dos campos que devem ser considerados durante a busca.
        Junto do nome do campo está o peso que ele possui na busca, separado por "^". 
        
        No exemplo abaixo, os termos casados no campo título possuem o dobro do peso dos
        termos casados no campo conteúdo:
        ['titulo^2', 'conteudo^1']
        '''

        result_list = []
        for item in cls.get_fields(searchable=True):
            result_list.append(item['field_name']+'^'+str(item['weight']))
        return result_list
    

    @classmethod
    def retrievable_fields(cls):
        '''
        Retorna uma lista com o nome dos campos que devem ser retornados durante a busca.
        
        NOTA: Repare na diferença com o método "searchable_fields" acima. Aqui listamos todos 
        os campos que devem ser retornados, alguns não fazem parte da busca, mas contém 
        informações que precisam ser recuperadas.
        '''

        result_list = []
        for item in cls.get_fields(retrievable=True):
            result_list.append(item['field_name'])
        return result_list
    

    @classmethod
    def get_fields(cls, searchable=None, retrievable=None):
        '''
        Retorna uma lista de campos. Passe searchable ou retrievable para filtrar.
        '''

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_FIELDS)
        if searchable != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "searchable": True }}))
        if retrievable != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "retrievable": True }}))
        elastic_result = search_obj.execute()

        result_list = []
        for item in elastic_result:
            result_list.append(dict({'id': item.meta.id}, **item.to_dict()))
        return result_list
    
    # CONFIGURAÇÕES DOS ÍNDICES ######################################################################

    @classmethod
    def searchable_indices(cls, group=None):
        '''
        Retorna uma lista com o nome dos índices do elasticsearch que devem ser
        considerados durante a busca
        '''

        indices = []
        for item in cls.get_indices(group=group, active=True):
            indices.append(item['es_index_name'])
        return indices
    
    @classmethod
    def searchable_index_to_class(cls, group=None):
        '''
        Retorna um dicionário relacionando o nome do índice no elasticsearch
        com a referência para classe Python que o representa
        '''

        index_to_class = {}
        for item in cls.get_indices(group=group, active=True):
            index_to_class[item['es_index_name']] = eval(item['class_name'])
        return index_to_class

    
    @classmethod
    def get_indices(cls, group=None, active=None):
        '''
        Retorna a lista de índices. Passe group e active para filtrar.
        Cada item da lista contém:
        - id: ID do registro no elastic
        - ui_name: nome do índice para ser exibido para o usuário
        - es_index_name: nome do índice no elasticsearch
        - class_name: nome da classe python que cuida do índice
        - group: grupo do índice ("regular" ou "replica")
        - active: indica se o índice está ativo para ser buscado
        '''

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_INDICES)
        if active != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "active": True }}))
        if group != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "group": group }}))

        elastic_result = search_obj.execute()
        result_list = []
        for item in elastic_result:
            result_list.append(dict({'id': item.meta.id}, **item.to_dict()))
        
        return result_list
    
    # CONFIGURAÇÕES DO MAPEAMENTO DAS ENTIDADES #########################################################

    @classmethod
    def entity_type_to_index_name(cls):
        total = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_ENTITIES).count()

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_ENTITIES)
        search_obj = search_obj[0:total]
        elastic_result = search_obj.execute()
        
        type2field = {}
        for item in elastic_result:
            type2field[item['entity_type']] = item['field_name']
        
        return type2field