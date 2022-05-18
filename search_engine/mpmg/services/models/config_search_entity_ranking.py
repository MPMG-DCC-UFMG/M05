from mpmg.services.models.elastic_model import ElasticModel

class ConfigSearchRankingEntity(ElasticModel):
    index_name = 'config_search_ranking_entity'

    def __init__(self, **kwargs):
        index_name = ConfigSearchRankingEntity.index_name
        
        meta_fields = ['id']

        index_fields = [
            'ativo',
            'nome',
            'tipo_entidade',
            'tecnica_agregacao',
            'tamanho_ranking'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
     
