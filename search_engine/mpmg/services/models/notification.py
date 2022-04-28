from mpmg.services.models.elastic_model import ElasticModel

class Notification(ElasticModel):
    index_name = 'notifications'

    def __init__(self, **kwargs):
        index_name = Notification.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'texto',
            'tipo',
            'data_criacao',
            'data_modificacao',
            'data_visualizacao',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def mark_as_visualized(self, notification_id, data_visualizacao):
        '''
        Atualiza uma notificação com a data em que ela foi visualizada.
        '''

        if self.get_by_id(notification_id)['data_visualizacao'] is not None:
            return False, 'A notificação já foi visualizada.'

        response = self.elastic.es.update(index=self.index_name, id=notification_id, body={
                                          "doc": {"data_visualizacao": data_visualizacao, }})

        success = response['result'] == 'updated'
        msg_error = ''

        if not success:
            msg_error = 'Não foi possível atualizar.'

        return success, msg_error
