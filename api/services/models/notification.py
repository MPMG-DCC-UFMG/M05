from services.models.elastic_model import ElasticModel

class Notification(ElasticModel):
    index_name = 'notifications'

    def __init__(self, **kwargs):
        index_name = Notification.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'texto',
            'tipo',
            'nome_cliente_api',
            'data_criacao',
            'data_modificacao',
            'data_visualizacao',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)