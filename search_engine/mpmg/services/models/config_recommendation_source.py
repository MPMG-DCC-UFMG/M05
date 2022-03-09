from operator import index
from mpmg.services.models import ElasticModel

class ConfigRecommendationSource(ElasticModel):
    index_name = 'config_recommendation_sources'

    def __init__(self, **kwargs):
        index_name =  ConfigRecommendationSource.index_name
        meta_fields =  ['id']
        index_fields = [
            'ui_name',
            'es_index_name',
            'amount',
            'active',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)