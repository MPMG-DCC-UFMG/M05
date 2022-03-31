from datetime import datetime
from time import time
import numpy as np
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import DocumentRecommendation, ConfigRecommendationEvidence, Notification


class DocumentRecommendationView(APIView):
    '''
    get:
        description: Retorna a lista de recomendações de um usuário. Se o ID da notificação que gerou as recomendações for passado, só elas serão retornadas.
        parameters:
            - name: user_id
              in: query
              description: ID do usuário
              required: true
              schema:
                    type: string
            - name: notification_id
              in: query
              description: ID da notificação que gerou a recomendação.
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna uma lista de recomendações.
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: integer
                                        description: ID da recomendação.
                                    user_id:
                                        type: string
                                        description: ID do usuário que recebeu a recomendação.
                                    notification_id: 
                                        type: string
                                        description: ID da notificação que a recomendação está associada.
                                    recommended_doc_index:
                                        type: string
                                        description: Índice do documento recomendado.
                                    recommended_doc_id:
                                        type: string
                                        description: ID do documento recomendado.
                                    recommended_doc_title:
                                        type: string
                                        description: Título do documento recomendado.
                                    matched_from:
                                        type: string
                                        description: De onde a recomendação foi baseada, podendo ser click, bookmark ou query. 
                                    evidence_query_text:
                                        type: string
                                        description: Se a origem da recomendação foi uma consulta, ela aparecerá aqui.
                                    evidence_doc_index:
                                        type: string
                                        description: Se a origem da recomendação foi um favorito, será o índice do documento favoritado.
                                    evidence_doc_id: 
                                        type: string
                                        description: Se a origem da recomendação foi um favorito, será o ID do documento favoritado.
                                    evidence_doc_title:
                                        type: string
                                        description: Se a origem da recomendação foi um favorito, será o título do documento favoritado.
                                    date: 
                                        type: integer
                                        description: Timestamp de quando a recomendação foi feita.
                                    similarity_value:
                                        type: number
                                        description: O quão similar é o documento recomendado e os que serviram de base para a recomendação.
                                    accepted: 
                                        type: boolean
                                        nullable: true
                                        description: Informa se o usuário aceitou ou não a recomendação.
                                    date_visualized: 
                                        type: integer
                                        nullable: true
                                        description: Timestamp de quando o usuário visualizou a
    post:
        description: Processa novas recomendações de documentos para um usuário específico ou todos.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            user_id:
                                description: ID do usuário que receberá as recomendações. Deixe em branco para recomendar para todos os usuários.
                                type: string
        responses:
            '201':
                description: As recomendações foram feitas para o usuário específico ou todos.

    put:
        description: Atualiza o status de uma recomendação para visualizado e/ou se o usuário a aprovou.
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
                                description: booleando indicando se o usuário aprovou a recomendação. Caso não haja opinião, passar o campo em branco.
                                type: boolean
                                nullable: true
                            date_visualized:
                                description: Inteiro representando o timestamp de quando a recomendação foi vista. Se em branco, o próprio sistema preencherá o campo.
                                type:
                                    - int
                        required:
                            - recommendation_id
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.

    delete:
        description: Apaga uma recomendação.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            recommendation_id:
                                description: ID da recomendação a ser removida.
                                type: string
                        required:
                            - recommendation_id      
        responses:
            '204':
                description: A notificação foi removida com sucesso.
            '500':
                description: Houve algum(ns) erro(s) interno durante o processamento.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
    '''

    schema = AutoDocstringSchema()
    config_rec_evidences = ConfigRecommendationEvidence()
    
    def _cosine_similarity(self, doc1, doc2):
        return np.dot(doc2, doc2)/(np.linalg.norm(doc1)*np.linalg.norm(doc2))
    
    def get(self, request):
        user_id = request.GET['user_id']

        notification_id = request.GET.get('notification_id')
        if notification_id:
            recommendations_list = DocumentRecommendation().get_by_notification_id(notification_id=notification_id)

        else:
            recommendations_list = DocumentRecommendation().get_by_user(user_id=user_id)
        
        return Response(recommendations_list, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        user_id = request.POST.get('user_id', None)
        document_recommendation =  DocumentRecommendation()
        notification = Notification()

        if user_id == None or user_id == '':
            users_ids = document_recommendation.get_users_ids_to_recommend()

        else:
            users_ids = [user_id]

        # data da última recomendação de cada usuário
        user_dates = document_recommendation.get_last_recommendation_date()


        # quais os tipos de evidência que devem ser usadas na recomendação
        config_evidences, _ = self.config_rec_evidences.get(active=True)

        for user_id in users_ids:

            # usa como data de referência a data da última recomendação
            # se o usuário não possui data, usa a semana anterior como data de referência
            if user_id in user_dates:
                reference_date = user_dates[user_id]
                
            else:
                reference_date = '2021-04-01'

            # busca os documentos candidatos a recomendação
            candidates = document_recommendation.get_candidate_documents(reference_date)

            valid_recommendations = []

            for evidence_item in config_evidences:
                top_n = evidence_item['top_n_recommendations']
                min_similarity = evidence_item['min_similarity']

                # busca as evidências do(s) usuário(s)
                user_evidences = document_recommendation.get_evidences(user_id, evidence_item['evidence_type'], evidence_item['es_index_name'], evidence_item['amount'])

                # computa a similaridade entre os documentos candidatos e a evidência
                similarity_ranking = []

                evidence_ranking = dict()
                for evidence_i, evidence_doc in enumerate(user_evidences):
                    if evidence_i not in evidence_ranking:
                        evidence_ranking[evidence_i] = []

                    for candidate_i, candidate_doc in enumerate(candidates):
                        similarity_score = self._cosine_similarity(candidate_doc['embedding_vector'], evidence_doc['embedding_vector']) * 100
                        if similarity_score >= min_similarity:
                            evidence_ranking[evidence_i].append((candidate_i, similarity_score, evidence_i))
                    
                    evidence_ranking[evidence_i].sort(key = lambda item: item[1], reverse=True)

                num_docs_recommended_in_evidence = 0
                while True:
                    candidate_rankings = []
                    for evidence_i_candidates in evidence_ranking.values():
                        if len(evidence_i_candidates) > 0:
                            candidate_rankings.append(evidence_i_candidates.pop(0))
                    candidate_rankings.sort(key = lambda item: item[1], reverse=True)

                    if len(candidate_rankings) == 0:
                        break

                    for i in range(min(top_n - num_docs_recommended_in_evidence, len(candidate_rankings))):
                        num_docs_recommended_in_evidence += 1
                        
                        candidate_i, score, evidence_i = candidate_rankings[i]

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
                            'date': int(time() * 1000),
                            'similarity_value': score,
                            'accepted': None
                        })

                        del candidates[candidate_i]

                        if num_docs_recommended_in_evidence == top_n:
                            break

                    if num_docs_recommended_in_evidence == top_n:
                            break        
                
            # se existem recomendações válidas, cria uma notificação e associa o seu ID 
            # aos registros de recomendação antes de gravá-los
            if len(valid_recommendations) > 0:
                # cria a notificação
                notification_response = notification.create({
                    'user_id': user_id,
                    'message': 'Novos documentos que possam ser do seu interesse.',
                    'type': 'RECOMMENDATION',
                    'date': int(time() * 1000)
                })
                notification_id = notification_response['_id']

                for recommendation in valid_recommendations:
                    recommendation['notification_id'] = notification_id
                    document_recommendation.save(recommendation)


        return Response(status=status.HTTP_201_CREATED)
    
    def put(self, request):
        data = request.data.dict()

        recommendation_id = data['recommendation_id']
        if 'accepted' not in data and 'date_visualized' not in data:
            return Response({'message': 'É necessário informar o campo accepted ou date_visualized.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'accepted' in data:
            accepted = data['accepted']
            if accepted == 'True' or accepted == 'true':
                accepted = True
            
            elif accepted == 'false' or accepted == 'False':
                accepted = False
            
            elif accepted == '':
                accepted = None

            else:
                return Response({'message': 'Não foi possível realizar o parsing dos parâmetros passados.'}, status.HTTP_400_BAD_REQUEST)

            success, msg_error = DocumentRecommendation().update_feedback(recommendation_id, accepted)
            if not success:
                return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST)
            
        
        if 'date_visualized' in data:
            date_visualized = data.get('date_visualized')
            if not date_visualized:
                date_visualized = int(time() * 1000)
            
            success, msg_error = DocumentRecommendation().mark_as_seen(recommendation_id, date_visualized)
            if not success:
                return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        data = request.data.dict()

        recommendation_id = data.get('recommendation_id')
        if recommendation_id is None:
            return Response({'message': 'Informe o ID da notificação deletada.'}, status.HTTP_400_BAD_REQUEST)
        
        success, msg_error = DocumentRecommendation().remove(recommendation_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        matched_from = ['query', 'bookmark', 'click', 'bookmark', 'bookmark', 'query', 'bookmark', 'click', 'query', 'query']
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
                'original_doc_index': ref_docs[i][1] if matched_from[i] != 'query' else '',
                'original_doc_id': ref_docs[i][0] if matched_from[i] != 'query' else '',
                'date': '2021-01-01',
                'similarity_value': '0.80',
                'accepted': '',
            }
            elastic.es.index(index='doc_recommendations', body=body)