from services.models import ElasticModel

class City(ElasticModel): 
    index_name = 'cidades'

    def __init__(self, **kwargs):
        index_name = City.index_name
        meta_fields = ['id']

        index_fields = [
            'codigo_cidade',
            'nome_cidade',
            'nome_estado',
            'sigla_estado',
            'codigo_estado',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
