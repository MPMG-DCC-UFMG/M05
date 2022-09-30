from mpmg.services.models.elastic_model import ElasticModel

class ProconCategory(ElasticModel):
    index_name = 'procon_categorias'

    def __init__(self, **kwargs):
        index_name = ProconCategory.index_name
        meta_fields = ['id']
        index_fields = [
            'categoria'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
