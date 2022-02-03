from mpmg.services.elastic import Elastic


class ConfigRecommendation:


    elastic = Elastic()
    INDEX_CONFIG_RECOMMENDATION_SOURCES = 'config_recommendation_sources'
    INDEX_CONFIG_RECOMMENDATION_EVIDENCES = 'config_recommendation_evidences'
    def __init__(self, **kwargs):
        None
    

    @classmethod
    def get_sources(cls, active=None):
        '''
        Retorna a lista de fontes de recomendação. Cada fonte contém:
            ui_name - nome da fonte a ser exibida para o usuário
            es_index_name - nome do índice no elasticsearch
            amount - qtde máxima de documentos que devem ser selecionados
            active - se a fonte está ativa para ser usada ou não
        '''
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_RECOMMENDATION_SOURCES)
        if active != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "active": active }}))
        elastic_result = search_obj.execute()
        
        sources = []
        for item in elastic_result:
            sources.append(dict({'id': item.meta.id}, **item.to_dict()))
        
        return sources
    
    
    @classmethod
    def update_sources(cls):
        return None
    

    @classmethod
    def get_evidences(cls, active=None):
        '''
        Retorna a lista de evidências para recomendação. Cada item da lista contém:
            ui_name - Nome da evidência a ser exibida para o usuário
            evidence_type - string representando uma constante com o tipo da evidência
            es_index_name - nome do índice onde os dados da evidência serão buscados
            amount - Qtde de itens daquela evidência que devem ser levadas em conta para comnputar a recomendação
            min_similarity - Valor do score que a similaridade entre a evidência e o documento deve alcançar para ser recomendada (1 a 100)
            top_n_recommendations - Qtde de documentos que devem ser recomendados ao combinar com aquela evidência
            active - Se a evidência deve ser considerada no algoritmo de recomendação
        '''
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.INDEX_CONFIG_RECOMMENDATION_EVIDENCES)
        if active != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q({"term": { "active": active }}))
        elastic_result = search_obj.execute()
        
        evidences = []
        for item in elastic_result:
            evidences.append(dict({'id': item.meta.id}, **item.to_dict()))
        
        return evidences
    

    @classmethod
    def update_evidences(cls):
        return None