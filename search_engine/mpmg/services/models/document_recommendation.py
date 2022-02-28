from time import time
from mpmg.services.models.elastic_model import ElasticModel
from .config_recommendation import ConfigRecommendation
from collections import defaultdict
from ..semantic_model import SemanticModel


class DocumentRecommendation(ElasticModel):
    index_name = 'doc_recommendations'
    
    def __init__(self, **kwargs):
        index_name = DocumentRecommendation.index_name
        meta_fields = ['id']
        index_fields = [
            'user_id',
            'notification_id',
            'recommended_doc_index',
            'recommended_doc_id',
            'recommended_doc_title',
            'matched_from',
            'evidence_query_text',
            'evidence_doc_index',
            'evidence_doc_id',
            'evidence_doc_title',
            'date',
            'similarity_value',
            'accepted',
            'date_visualized'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    

    def get_by_user(self, user_id):
        '''
        Retorna a lista de recomendações do usuário.
        '''
        
        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)
        search_obj = search_obj.query(self.elastic.dsl.Q({"term": { "user_id": user_id }}))
        
        # faz a consulta uma vez pra pegar o total de resultados
        parcial_result = search_obj.execute()
        total_records = parcial_result.hits.total.value

        # refaz a consulta trazendo todos os resultados
        search_obj = search_obj[0:total_records]
        search_obj = search_obj.sort({'date':{'order':'desc'}})
        total_result = search_obj.execute()

        recommendations_list = []
        for item in total_result:
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            
            recommendations_list.append(DocumentRecommendation(**dict_data))
        
        return recommendations_list

    def get_by_notification_id(self, notification_id):
        '''
        Retorna as recomendações geradas no id da notificação passada.
        '''

        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)        
        search_obj = search_obj.query(self.elastic.dsl.Q({"term": { "notification_id.keyword": notification_id }}))

        # faz a consulta uma vez pra pegar o total de segmentos
        parcial_result = search_obj.execute()
        total_records = parcial_result.hits.total.value

        # refaz a consulta trazendo todos os resultados
        search_obj = search_obj[0:total_records]
        search_obj = search_obj.sort({'date':{'order':'desc'}})
        total_result = search_obj.execute()

        recommendations_list = []
        for item in total_result:
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            
            recommendations_list.append(DocumentRecommendation(**dict_data))
        
        return recommendations_list
    
    def update_feedback(self, recommendation_id, accepted):
        '''
        Atualiza o campo accepted, indicando se o usuário aprovou ou não aquela recomendação.
        '''

        response = self.elastic.es.update(index=self.index_name, id=recommendation_id, body={"doc": {"accepted": accepted, }})

        success = response['result'] == 'updated' 
        msg_error = ''
        if not success:
            msg_error = 'Não foi possível atualizar.'

        return success, msg_error

    def mark_as_seen(self, recommendation_id, date_visualized):
        '''
        Atualiza o campo accepted, indicando se o usuário aprovou ou não aquela recomendação.
        '''
        response = self.elastic.es.update(index=self.index_name, id=recommendation_id, body={"doc": {"date_visualized": date_visualized}})

        success = response['result'] == 'updated' 
        msg_error = ''
        if not success:
            msg_error = 'Não foi possível atualizar.'

        return success, msg_error

    def get_users_ids_to_recommend(self):
        '''
        Retorna uma lista com todos os user_ids da API para fazer a recomendação.
        Como a API não controla os usuários (quem controla é o WSO2),
        iremos buscar os IDs consultando os logs
        '''

        users_ids = []
        # busca todos os IDs, varrendo os índices de logs de buscas e bookmarks
        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=['log_buscas', 'bookmark'])
        search_obj = search_obj.extra(size=0) # não precisa retornar documentos, apenas a agregação
        search_obj.aggs.bucket('ids_usuarios', 'terms', field='id_usuario.keyword')
        elastic_result = search_obj.execute()
        for item in elastic_result['aggregations']['ids_usuarios']['buckets']:
            users_ids.append(item['key'])
        
        return users_ids
    

    def get_last_recommendation_date(self, user_id=None):
        '''
        Retorna um dicionário do tipo user_id:date que contém a data da última
        recomendação de cada usuário. Os documentos candidatos devem ter data de
        indexação posterior à data da última recomendação
        '''

        date_by_user = {}
        # search_obj = self.elastic.dsl.Search(using=self.elastic.es, index='doc_recommendations')
        # return date_by_user
        return {'1': '2021-04-01', '2': '2021-05-01'}


    
    def get_candidate_documents(self, reference_date) -> list:
        '''
        Retorna uma lista de documentos candidatos para serem recomendados.
        Os documentos devem ter a data de indexação posterior à reference_date

        A quantidade de documentos e os tipos dos documentos dependem da
        configuração salva em config_recommendation_sources.

        Esta lista é usado pelo algoritmo de recomendação definido na view
        document_recommendation
        '''

        # qtde e tipo dos documentos candidatos
        sources = ConfigRecommendation.get_sources(active=True)
        
        candidates_keys = set()
        candidates = []
        for item in sources:
            index_name = item['es_index_name']
            amount = item['amount']
            
            search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=index_name)
            search_obj = search_obj.query("bool", filter = [self.elastic.dsl.Q({'range': {'data_indexacao': {'gte': reference_date }}})])
            search_obj = search_obj[0:amount]
            elastic_result = search_obj.execute()

            for item in elastic_result:
                key = f'{index_name}:{item.meta.id}'
                if key not in candidates_keys:
                    candidates.append({'id': item.meta.id, 'index_name':index_name, 'title': item['titulo'], 'embedding_vector': item['embedding_vector']})
                    candidates_keys.add(key)
                    
        return candidates
    

    def get_evidences(self, user_id, evidence_type, evidence_index, amount):
        '''
        Retorna uma lista de evidências do usuário para servir como base de recomendação.
        As evidências podem ser 3:
            - QUERY: Texto de consultas executadas anteriormente pelo usuário
            - CLICK: Documentos clicados pelo usuário anteriormente
            - BOOKMARK: Documentos marcados como favoritos
        '''

        semantic_model = SemanticModel()
        
        user_evidences = []

        # TODO: Padronizar o nome destes campos
        if evidence_type == 'QUERY':
            date_field = 'data_hora'
        elif evidence_type == 'CLICK':
            date_field = 'timestamp'
        elif evidence_type == 'BOOKMARK':
            date_field = 'data_criacao'

        # busca as evidências do usuário
        search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=evidence_index
        )
        search_obj = search_obj.query(self.elastic.dsl.Q({'match_phrase': {'id_usuario.keyword': user_id}}))

        # print('*' * 15)
        # print(search_obj.execute())
        # print('*' * 15)

        search_obj = search_obj.sort({date_field:{'order':'desc'}})
        search_obj = search_obj[0:amount]
        elastic_result = search_obj.execute()


        # se for consulta, pega o texto da consulta e passa pelo modelo para obter o embedding
        if evidence_type == 'QUERY':
            for doc in elastic_result:
                embbeded_query = semantic_model.get_dense_vector(doc['text_consulta'])
                user_evidences.append({'id':None, 'index_name':None, 'title':None, 'query': doc['text_consulta'], 'embedding_vector': embbeded_query})
        

        # se for click, pega os IDs dos documentos clicados e faz uma nova consulta 
        # para recuperar o embedding destes documentos
        elif evidence_type == 'CLICK':
            # pega o ID dos documentos clicados e o índice a qual cada um pertence
            doc_ids_by_type = defaultdict(list)
            for doc in elastic_result:
                
                doc_type = doc['tipo_documento']
                doc_id = doc['id_documento']
                print(f'{doc_type}:{doc_id}')
                doc_ids_by_type[doc_type].append(doc_id)
            # pega os embeddings dos documentos clicados através dos IDs no respectivo índice
            for dtype, ids in doc_ids_by_type.items():
                evidence_docs = self.elastic.dsl.Document.mget(ids, using=self.elastic.es, index=dtype)
                for doc in evidence_docs:
                    if doc != None:
                        user_evidences.append({'id':doc.meta.id, 'index_name': dtype, 'title':doc['titulo'], 'query': None, 'embedding_vector': doc['embedding_vector']})
        

        # se for bookmark, pega os IDs dos documentos favoritados e faz uma nova consulta 
        # para recuperar o embedding destes documentos
        elif evidence_type == 'BOOKMARK':
            # pega o ID dos documentos favoritados e o índice a qual cada um pertence
            doc_ids_by_type = defaultdict(list)
            for doc in elastic_result:
                doc_type = doc['indice_documento']
                doc_id = doc['id_documento']

                print(f'{doc_type}:{doc_id}')

                doc_ids_by_type[doc_type].append(doc_id)
            # pega os embeddings dos documentos favoritados através dos IDs no respectivo índice
            for dtype, ids in doc_ids_by_type.items():
                evidence_docs = self.elastic.dsl.Document.mget(ids, using=self.elastic.es, index=dtype)
                for doc in evidence_docs:
                    if doc != None:
                        user_evidences.append({'id':doc.meta.id, 'index_name': dtype, 'title':doc['titulo'], 'query': None, 'embedding_vector': doc['embedding_vector']})
        
        return user_evidences




            


