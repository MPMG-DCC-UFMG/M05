from mpmg.services.elastic import Elastic
from mpmg.services.models import Processo, Diario, DiarioSegmentado, Licitacao
from mpmg.services.models.reclame_aqui import ReclameAqui

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
    INDEX_CONFIG_RANKING_ENTITY = 'config_ranking_entity'
    INDEX_CONFIG_FILTER_BY_ENTITY = 'config_filter_by_entity'

    def __init__(self, **kwargs):
        None


    # CONFIGURAÇÕES DAS OPÇÕES ######################################################################

    @classmethod
    def use_semantic_vectors_in_search(cls, api_client_name):
        return cls.get_options(api_client_name)['use_semantic_vectors_in_search']
    
    @classmethod
    def identify_entities_in_query(cls, api_client_name):
        return cls.get_options(api_client_name)['identify_entities_in_query']
    
    @classmethod
    def highlight_field(cls, api_client_name):
        return cls.get_options(api_client_name)['highlight_field']
    
    @classmethod
    def results_per_page(cls, api_client_name):
        return cls.get_options(api_client_name)['results_per_page']


    @classmethod
    def get_options(cls, api_client_name):
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_OPTIONS)
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        elastic_result = search_obj.execute()
        item = elastic_result[0]
        options = dict({'id': item.meta.id}, **item.to_dict())
        return options
    
    @classmethod
    def update_options(cls, item_id, results_per_page, highlight_field, identify_entities_in_query, use_semantic_vectors_in_search):
        return cls.elastic.es.update(index=cls.INDEX_CONFIG_OPTIONS, 
                                     doc_type='_doc',
                                     id=item_id, 
                                     body={"doc": 
                                            {
                                                "results_per_page": results_per_page, 
                                                "highlight_field": highlight_field,
                                                "identify_entities_in_query": identify_entities_in_query,
                                                "use_semantic_vectors_in_search": use_semantic_vectors_in_search,
                                            }})
    
    
    # CONFIGURAÇÕES DOS CAMPOS ######################################################################
    
    @classmethod
    def searchable_fields(cls, api_client_name):
        '''
        Retorna uma lista com o nome dos campos que devem ser considerados durante a busca.
        Junto do nome do campo está o peso que ele possui na busca, separado por "^". 
        
        No exemplo abaixo, os termos casados no campo título possuem o dobro do peso dos
        termos casados no campo conteúdo:
        ['titulo^2', 'conteudo^1']
        '''

        result_list = []
        for item in cls.get_fields(api_client_name, searchable=True):
            result_list.append(item['field_name']+'^'+str(item['weight']))
        return result_list
    

    @classmethod
    def retrievable_fields(cls, api_client_name):
        '''
        Retorna uma lista com o nome dos campos que devem ser retornados durante a busca.
        
        NOTA: Repare na diferença com o método "searchable_fields" acima. Aqui listamos todos 
        os campos que devem ser retornados, alguns não fazem parte da busca, mas contém 
        informações que precisam ser recuperadas.
        '''

        result_list = []
        for item in cls.get_fields(api_client_name, retrievable=True):
            result_list.append(item['field_name'])
        return result_list
    

    @classmethod
    def get_fields(cls, api_client_name, searchable=None, retrievable=None):
        '''
        Retorna uma lista de campos. Passe searchable ou retrievable para filtrar.
        '''

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_FIELDS)
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        if searchable != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "searchable": True }}))
        if retrievable != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "retrievable": True }}))
        search_obj = search_obj.sort({'_id':{'order':'asc'}})
        elastic_result = search_obj.execute()

        result_list = []
        for item in elastic_result:
            result_list.append(dict({'id': item.meta.id}, **item.to_dict()))
        return result_list
    

    @classmethod
    def update_field(cls, item_id, searchable, weight):
        '''
        Atualiza o peso e se o campo deve ser considerado na busca
        '''
        return cls.elastic.es.update(index=cls.INDEX_CONFIG_FIELDS, doc_type='_doc',id=item_id, body={"doc": {"searchable": searchable, "weight": weight }})
        
    
    # CONFIGURAÇÕES DOS ÍNDICES ######################################################################

    @classmethod
    def searchable_indices(cls, api_client_name, group=None):
        '''
        Retorna uma lista com o nome dos índices do elasticsearch que devem ser
        considerados durante a busca
        '''

        indices = []
        for item in cls.get_indices(api_client_name, group=group, active=True):
            indices.append(item['es_index_name'])
        return indices
    
    @classmethod
    def searchable_index_to_class(cls, api_client_name, group=None):
        '''
        Retorna um dicionário relacionando o nome do índice no elasticsearch
        com a referência para classe Python que o representa
        '''

        index_to_class = {}
        for item in cls.get_indices(api_client_name, group=group, active=True):
            index_to_class[item['es_index_name']] = eval(item['class_name'])
        return index_to_class

    
    @classmethod
    def get_indices(cls, api_client_name, group=None, active=None):
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
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        if active != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "active": True }}))
        if group != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "group": group }}))
        search_obj = search_obj.sort({'_id':{'order':'asc'}})

        elastic_result = search_obj.execute()
        result_list = []
        for item in elastic_result:
            result_list.append(dict({'id': item.meta.id}, **item.to_dict()))
        
        return result_list
    
    @classmethod
    def get_total(cls, api_client_name: str, index_name: str) -> int:
        '''
        Retorna o total de registros salvos no índice para um cliente específico da API.
        '''
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=index_name)
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        total = search_obj.count()
        return total

    @classmethod
    def get_config_ranking_entity(cls, api_client_name):
        '''
        Retorna uma lista com as configurações de ranqueamento pra cada tipo de entidade.
        Cada item da lista contém:
         - id: ID do registro no elastic
         - nome: Nome do tipo da entidade para ser exibido para o usuário
         - tipo_entidade: Tipo da entidade, pra ser usado internamento no código
         - tecnica_agregacao: Nome da agregação usada para fazer o ranking
         - tamanho_ranking: Número de entidades que farão parte do ranking
         - ativo: Indica se o tipo de entidade em questão deve ser ranqueada ou não
        '''

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_RANKING_ENTITY)
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        total = cls.get_total(api_client_name, cls.INDEX_CONFIG_RANKING_ENTITY)
        search_obj = search_obj[0:total]
        search_obj = search_obj.sort({'_id': {'order': 'asc'}})
        elastic_result = search_obj.execute()

        result_list = []
        for item in elastic_result:
            result_list.append(dict({'id': item.meta.id}, **item.to_dict()))
        return result_list

    @classmethod
    def update_config_ranking_entity(cls, item_id: str, active: bool, aggregation_type: str, ranking_size: int) -> list:
        ''' 
        Permite atualizar os campos `ativo`, `tecnica_agregacao` e `tamanho_ranking` de uma configuração de ranking de entidade.
        '''
        updated_fields = {
            'ativo': active,
            'tecnica_agregacao': aggregation_type,
            'tamanho_ranking': ranking_size
        }
        
        cls.elastic.es.update(index=cls.INDEX_CONFIG_RANKING_ENTITY, doc_type='_doc', id=item_id, body={"doc": updated_fields})

    @classmethod
    def config_filter_by_entities(cls, api_client_name):
        '''
        Retorna uma lista com as configurações de tipos de entidades que podem ser usadas como filtro de consulta
        Cada item da lista contém:
         - id: ID do registro no elastic
         - nome: Nome do tipo da entidade para ser exibido para o usuário
         - tipo_entidade: Tipo da entidade, pra ser usado internamento no código
         - tecnica_agregacao: Nome da agregação usada para fazer o filtro
         - tamanho_ranking: Número de entidades que farão parte do filtro
         - ativo: Indica se o tipo de entidade em questão deve ser usada como filtro ou não
        '''

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_FILTER_BY_ENTITY)
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        total = cls.get_total(api_client_name, cls.INDEX_CONFIG_FILTER_BY_ENTITY)
        search_obj = search_obj[0:total]
        search_obj = search_obj.sort({'_id': {'order': 'asc'}})
        elastic_result = search_obj.execute()

        result_list = []
        for item in elastic_result:
            result_list.append(dict({'id': item.meta.id}, **item.to_dict()))

        return result_list

    @classmethod
    def update_config_filter_by_entity(cls, item_id: str, active: bool, aggregation_type: str, num_entities: int):
        ''' 
        Permite atualizar os campos `ativo`, `tecnica_agregacao` e `num_entidades` de uma configuração de filtro por entidades.
        '''
        updated_fields = {
            'ativo': active,
            'tecnica_agregacao': aggregation_type,
            'num_entidades': num_entities
        }
        
        cls.elastic.es.update(index=cls.INDEX_CONFIG_FILTER_BY_ENTITY,
                              doc_type='_doc', id=item_id, body={"doc": updated_fields})
 
    @classmethod
    def update_active_indices(cls, ids, active):
        '''
        Atualiza o campo 'active' para True ou False dos registros listados em ids
        '''

        results = []
        for item_id in ids:
            result = cls.elastic.es.update(index=cls.INDEX_CONFIG_INDICES, doc_type='_doc',id=item_id, body={"doc": {"active": active }})
            results.append(result)
        
        return results

    
    
    # CONFIGURAÇÕES DO MAPEAMENTO DAS ENTIDADES #########################################################

    @classmethod
    def entity_type_to_index_name(cls, api_client_name):
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_ENTITIES)
        search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "nome_cliente_api": api_client_name}}))
        total = cls.get_total(api_client_name, cls.INDEX_CONFIG_ENTITIES)
        search_obj = search_obj[0:total]
        elastic_result = search_obj.execute()
        
        type2field = {}
        for item in elastic_result:
            type2field[item['entity_type']] = item['field_name']
        
        return type2field