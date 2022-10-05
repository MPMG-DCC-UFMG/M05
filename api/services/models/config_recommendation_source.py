from ctypes import Union
from services.models import ElasticModel

class ConfigRecommendationSource(ElasticModel):
    index_name = 'config_recommendation_sources'

    def __init__(self, **kwargs):
        index_name = ConfigRecommendationSource.index_name
        meta_fields = ['id']
        index_fields = [
            'nome',
            'nome_cliente_api',
            'nome_indice',
            'quantidade',
            'ativo',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get(self, api_client_name: str, source_id: str = None, active: bool = None):
        if source_id:
            return super().get(source_id)
            
        else:
            conf_sources_filter = [{'term': {'nome_cliente_api': api_client_name}}]
            if active is not None:
                conf_sources_filter.append({'term': {'ativo': active}}) 
            _, conf_sources_found = super().get_list(filter=conf_sources_filter, page='all')
            return conf_sources_found