from ctypes import Union
from services.models import ElasticModel

class ConfigLearningToRank(ElasticModel):
    index_name = 'config_learning_to_rank'

    def __init__(self, **kwargs):
        index_name = ConfigLearningToRank.index_name
        meta_fields = ['id']
        index_fields = [
            'modelo',
            'quantidade',
            'ativo',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)