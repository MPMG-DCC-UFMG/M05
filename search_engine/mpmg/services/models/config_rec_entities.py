from mpmg.services.models.elastic_model import ElasticModel

class ConfigRecEntity(ElasticModel):
    index_name = 'config_rec_entities'

    def __init__(self, **kwargs):
        index_name = ConfigRecEntity.index_name
        
        meta_fields = ['id']

        index_fields = [
            'ativo',
            'nome',
            'tipo_entidade',
            'tecnica_agregacao',
            'num_itens_recomendados'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
     
