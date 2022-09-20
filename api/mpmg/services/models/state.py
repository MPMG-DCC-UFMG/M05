from mpmg.services.models import ElasticModel

class State(ElasticModel): 
    index_name = 'estados'

    def __init__(self, **kwargs):
        index_name = State.index_name
        meta_fields = ['id']

        index_fields = [
            'codigo',
            'sigla',
            'nome',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
