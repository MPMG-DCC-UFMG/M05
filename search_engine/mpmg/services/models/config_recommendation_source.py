from mpmg.services.models import ElasticModel

class ConfigRecommendationSource(ElasticModel):
    index_name = 'config_recommendation_sources'

    def __init__(self, **kwargs):
        index_name = ConfigRecommendationSource.index_name
        meta_fields = ['id']
        index_fields = [
            'nome',
            'nome_indice',
            'quantidade',
            'ativo',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get(self, source_id=None, active=None):
        if source_id:
            return super().get(source_id)
            
        else:
            conf_sources_filter = {'term': {'ativo': active}} if active != None else None
            _, conf_sources_found = super().get_list(filter=conf_sources_filter, page='all')
            return conf_sources_found