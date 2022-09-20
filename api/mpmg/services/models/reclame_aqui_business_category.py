from mpmg.services.models.elastic_model import ElasticModel

class ReclameAquiBusinessCategory(ElasticModel):
    index_name = 'reclame_aqui_categorias_empresa'

    def __init__(self, **kwargs):
        index_name = ReclameAquiBusinessCategory.index_name
        meta_fields = ['id']
        index_fields = [
            'categoria'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
