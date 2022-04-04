from mpmg.services.models.elastic_model import ElasticModel


class Notification(ElasticModel):
    index_name = 'notifications'
    
    def __init__(self, **kwargs):
        index_name = Notification.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'mensagem',
            'tipo',
            'data_criacao',
            'data_visualizacao',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    

    def get_by_user(self, id_usuario):
        '''
        Retorna uma lista de notificações do usuário.
        '''
        
        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)
        
        search_obj = search_obj.query(self.elastic.dsl.Q({"term": { "id_usuario": id_usuario }}))
        search_obj = search_obj.sort({'data_criacao':{'order':'desc'}})
        elastic_result = search_obj.execute()

        notifications_list = []
        for item in elastic_result:
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            
            notifications_list.append(Notification(**dict_data))
        
        return notifications_list

    def get_by_id(self, notification_id):
        try:
            data = self.elastic.es.get(index=self.index_name, id=notification_id)['_source']
            data['id'] = notification_id
            return Notification(**data)
        
        except:
            None

    def mark_as_visualized(self, notification_id, data_visualizacao):
        '''
        Atualiza uma notificação com a data em que ela foi visualizada.
        '''

        if self.get_by_id(notification_id)['data_visualizacao'] is not None:
            return False, 'A notificação já foi visualizada.'

        response = self.elastic.es.update(index=self.index_name, id=notification_id, body={"doc": {"data_visualizacao": data_visualizacao, }})

        success = response['result'] == 'updated' 
        msg_error = ''
        if not success:
            msg_error = 'Não foi possível atualizar.'

        return success, msg_error