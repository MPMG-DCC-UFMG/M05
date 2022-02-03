from datetime import datetime
import numpy as np
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import DocumentRecommendation, ConfigRecommendation, Notification


class DocumentRecommendationView(APIView):
    '''
    get:
        description: Retorna a lista de recomendações de um usuário.
        parameters:
            - name: user_id
              in: query
              description: ID do usuário
              required: true
              schema:
                    type: string
    
    post:
        description: Processa novas recomendações de documentos para os usuários
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            user_id:
                                description: ID do usuário que receberá as recomendações. Deixe em branco para recomendar para todos os usuários.
                                type: string
    
    put:
        description: Atualiza a recomendação indicando se o usuário aprovou ou não a recomendação em questão.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            recommendation_id:
                                description: ID da recomendação a ser alterada.
                                type: string
                            accepted:
                                description: true ou false indicando se o usuário aprovou.
                                type: boolean
                        required:
                            - recommendation_id
                            - accepted
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.
    '''

    schema = AutoDocstringSchema()

    
    def _cosine_similarity(self, doc1, doc2):
        return np.dot(doc2, doc2)/(np.linalg.norm(doc1)*np.linalg.norm(doc2))
    
    def get(self, request):
        user_id = request.GET['user_id']
        
        recommendations_list = DocumentRecommendation().get_by_user(user_id=user_id)
        
        return Response(recommendations_list, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        user_id = request.POST.get('user_id', None)
        today = datetime.now().strftime('%Y-%m-%d')

        if user_id == None or user_id == '':
            users_ids = DocumentRecommendation().get_users_ids_to_recommend()
        else:
            users_ids = [user_id]

        # data da última recomendação de cada usuário
        user_dates = DocumentRecommendation().get_last_recommendation_date()


        # quais os tipos de evidência que devem ser usadas na recomendação
        config_evidences = ConfigRecommendation.get_evidences(active=True)


        for user_id in users_ids:

            # usa como data de referência a data da última recomendação
            # se o usuário não possui data, usa a semana anterior como data de referência
            if user_id in user_dates:
                reference_date = user_dates[user_id]
            else:
                reference_date = '2021-04-01'

            # busca os documentos candidatos a recomendação
            candidates = DocumentRecommendation().get_candidate_documents(reference_date)


            
            valid_recommendations = []
            for evidence_item in config_evidences:
                print(evidence_item['evidence_type'])
                top_n = evidence_item['top_n_recommendations']
                min_similarity = evidence_item['min_similarity']

                # busca as evidências do(s) usuário(s)
                user_evidences = DocumentRecommendation().get_evidences(user_id, evidence_item['evidence_type'], evidence_item['es_index_name'], evidence_item['amount'])
            
                # computa a similaridade entre os documentos candidatos e a evidência
                similarity_ranking = []
                for evidence_i, evidence_doc in enumerate(user_evidences):
                    for candidate_i, candidate_doc in enumerate(candidates):
                        similarity_score = self._cosine_similarity(candidate_doc['embedding_vector'], evidence_doc['embedding_vector'])
                        similarity_ranking.append({'evidence_i': evidence_i, 'candidate_i': candidate_i, 'score': similarity_score})
                similarity_ranking = list(sorted(similarity_ranking, key= lambda item: item['score'], reverse=True))
                
                # pega as top_n similares e verifica se são maiores ou iguais ao parâmetro min_similarity
                similarity_ranking = similarity_ranking[:top_n]
                for rank_item in similarity_ranking[:top_n]:
                    score = int(rank_item['score'] * 100)
                    candidate_i = rank_item['candidate_i']
                    evidence_i = rank_item['evidence_i']

                    print(score, min_similarity)
                    if score >= min_similarity:
                        valid_recommendations.append({
                            'user_id': user_id,
                            'notification_id': None,
                            'recommended_doc_index': candidates[candidate_i]['index_name'],
                            'recommended_doc_id': candidates[candidate_i]['id'],
                            'recommended_doc_title': candidates[candidate_i]['title'],
                            'matched_from': evidence_item['evidence_type'],
                            'evidence_query_text': user_evidences[evidence_i]['query'],
                            'evidence_doc_index': user_evidences[evidence_i]['index_name'],
                            'evidence_doc_id': user_evidences[evidence_i]['id'],
                            'evidence_doc_title': user_evidences[evidence_i]['title'],
                            'date': today,
                            'similarity_value': score,
                            'accepted': None
                        })
                        

            # se existem recomendações válidas, cria uma notificação e associa o seu ID 
            # aos registros de recomendação antes de gravá-los
            if len(valid_recommendations) > 0:
                # cria a notificação
                notification_response = Notification().create({
                    'user_id': user_id,
                    'message': 'Novos documentos que possam ser do seu interesse.',
                    'type': 'RECOMMENDATION',
                    'date': today
                })
                notification_id = notification_response['_id']

                for recommendation in valid_recommendations:
                    recommendation['notification_id'] = notification_id
                    response = DocumentRecommendation().save(recommendation)


        return Response({})
    

    def put(self, request):
        recommendation_id = request.POST['recommendation_id']
        accepted = request.POST['accepted']

        success, msg_error = DocumentRecommendation().update(recommendation_id, accepted)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_400_BAD_REQUEST)






class AddFakeRecommendationsView():
    '''
    CLASSE TEMPORÁRIA que adiciona recomendações para um determinado usuário
    para a execução de testes. Remova-a quando não for mais necessário
    
    Para executá-la siga os passos abaixo:

    1. Entre no shell do django: 
        python manage.py shell
    
    2. Execute:
        from mpmg.services.views.document_recommendation import AddFakeRecommendationsView
        AddFakeRecommendationsView().execute(1) # 1 é o user_id, altere de acordo
    '''

    def execute(self, user_id):        
        # antes de inserir, deleta as existentes
        from ..elastic import Elastic
        elastic = Elastic()
        search_obj = elastic.dsl.Search(using=elastic.es, index='doc_recommendations')
        search_obj = search_obj.query(elastic.dsl.Q({"term": { "user_id": user_id }}))
        search_obj.delete()

        # pega 10 documentos aleatoriamente para usar como recomendação
        from ..query import Query
        query = Query('maria', 1, '123', '456', user_id, 'regular')
        total_docs, total_pages, documents, response_time = query.execute()
        rec_docs = []
        for doc in documents:
            rec_docs.append((doc['id'], doc['type']))
        
        # pega 10 documentos aleatoriamente para usar como referência
        query = Query('joão', 1, '123', '456', user_id, 'regular')
        total_docs, total_pages, documents, response_time = query.execute()
        ref_docs = []
        for doc in documents:
            ref_docs.append((doc['id'], doc['type']))
        
        
        # insere as novas recomendações
        matched_from = ['QUERY', 'BOOKMARK', 'CLICK', 'BOOKMARK', 'BOOKMARK', 'QUERY', 'BOOKMARK', 'CLICK', 'QUERY', 'QUERY']
        queries = ['maria', '', '', '', '', 'covid', '', '', 'dengue', 'chuvas']
        for i, item in enumerate(rec_docs):
            doc_id, doc_type = item
            body = {
                'user_id': user_id,
                'notification_id': '',
                'recommended_doc_index': doc_id,
                'recommended_doc_id': doc_type,
                'matched_from': matched_from[i],
                'original_query_text': queries[i],
                'original_doc_index': ref_docs[i][1] if matched_from[i] != 'QUERY' else '',
                'original_doc_id': ref_docs[i][0] if matched_from[i] != 'QUERY' else '',
                'date': '2021-01-01',
                'similarity_value': '0.80',
                'accepted': '',
            }
            elastic.es.index(index='doc_recommendations', body=body)