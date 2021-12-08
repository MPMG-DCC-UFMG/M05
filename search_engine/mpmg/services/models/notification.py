from mpmg.services.models.elastic_model import ElasticModel


class Notification(ElasticModel):
    index_name = 'notifications'
    
    def __init__(self, **kwargs):
        index_name = Notification.index_name
        meta_fields = ['id']
        index_fields = [
            'user_id',
            'message',
            'type',
            'date',
            'date_visualized',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    

    def get_by_user(self, user_id):
        '''
        Retorna uma lista de notificações do usuário.
        '''
        
        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)
        
        search_obj = search_obj.query(self.elastic.dsl.Q({"term": { "user_id": user_id }}))
        search_obj = search_obj.sort({'date':{'order':'desc'}})
        elastic_result = search_obj.execute()

        notifications_list = []
        for item in elastic_result:
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            
            notifications_list.append(Notification(**dict_data))
        
        return notifications_list

    

    def mark_as_visualized(self, notification_id, date_visualized):
        '''
        Atualiza uma notificação com a data em que ela foi visualizada.
        '''

        response = self.elastic.es.update(index=self.index_name, id=notification_id, body={"doc": {"date_visualized": date_visualized, }})

        success = response['result'] == 'updated' 
        msg_error = ''
        if not success:
            msg_error = 'Não foi possível atualizar.'

        return success, msg_error
    
    