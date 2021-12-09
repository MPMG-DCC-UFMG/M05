from mpmg.services.models.elastic_model import ElasticModel


class DocumentRecomendation(ElasticModel):
    index_name = 'doc_recommendations'
    
    def __init__(self, **kwargs):
        index_name = DocumentRecomendation.index_name
        meta_fields = ['id']
        index_fields = [
            'user_id',
            'notification_id',
            'recommended_doc_index',
            'recommended_doc_id',
            'matched_from',
            'original_query_text',
            'original_doc_index',
            'original_doc_id',
            'date',
            'similarity_value',
            'accepted',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    

    def get_by_user(self, user_id):
        '''
        Retorna a lista de recomendações do usuário.
        '''
        
        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)
        
        search_obj = search_obj.query(self.elastic.dsl.Q({"term": { "user_id": user_id }}))
        search_obj = search_obj.sort({'date':{'order':'desc'}})
        elastic_result = search_obj.execute()

        recommendations_list = []
        for item in elastic_result:
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            
            recommendations_list.append(DocumentRecomendation(**dict_data))
        
        return recommendations_list


    def update(self, recommendation_id, accepted):
        '''
        Atualiza o campo accepted, indicando se o usuário aprovou ou não aquela recomendação.
        '''

        response = self.elastic.es.update(index=self.index_name, id=recommendation_id, body={"doc": {"accepted": accepted, }})

        success = response['result'] == 'updated' 
        msg_error = ''
        if not success:
            msg_error = 'Não foi possível atualizar.'

        return success, msg_error