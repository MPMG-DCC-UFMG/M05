from mpmg.services.models.elastic_model import ElasticModel

class ConfigFilterByEntity(ElasticModel):
    index_name = 'config_filter_ranking_entity'

    def __init__(self, **kwargs):
        index_name = ConfigFilterByEntity.index_name
        
        meta_fields = ['id']

        index_fields = [
            'ativo',
            'nome',
            'tipo_entidade',
            'tecnica_agregacao',
            'num_entidades'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
     
