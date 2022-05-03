from time import time

import numpy as np
from mpmg.services.models import (ConfigRecommendationEvidence,
                                  DocumentRecommendation, Notification)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

from mpmg.services.utils import validators, get_data_from_request, get_current_timestamp, str2bool 

DOC_REC = DocumentRecommendation()

class DocumentRecommendationView(APIView):
    '''
    get:
        description: Retorna a lista de recomendações de um usuário. Se o ID da notificação que gerou as recomendações for passado, só elas serão retornadas.
        parameters:
            - name: id_usuario
              in: query
              description: ID do usuário
              required: true
              schema:
                    type: string
            - name: id_notificacao
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
                                    id_usuario:
                                        type: string
                                        description: ID do usuário que recebeu a recomendação.
                                    id_notificacao: 
                                        type: string
                                        description: ID da notificação que a recomendação está associada.
                                    indice_doc_recomendado:
                                        type: string
                                        description: Índice do documento recomendado.
                                    id_doc_recomendado:
                                        type: string
                                        description: ID do documento recomendado.
                                    titulo_doc_recomendado:
                                        type: string
                                        description: Título do documento recomendado.
                                    evidencia:
                                        type: string
                                        description: De onde a recomendação foi baseada, podendo ser click, bookmark ou query. 
                                    evidencia_texto_consulta:
                                        type: string
                                        description: Se a origem da recomendação foi uma consulta, ela aparecerá aqui.
                                    evidencia_indice_doc:
                                        type: string
                                        description: Se a origem da recomendação foi um favorito, será o índice do documento favoritado.
                                    evidencia_id_doc: 
                                        type: string
                                        description: Se a origem da recomendação foi um favorito, será o ID do documento favoritado.
                                    evidencia_titulo_doc:
                                        type: string
                                        description: Se a origem da recomendação foi um favorito, será o título do documento favoritado.
                                    data_criacao: 
                                        type: integer
                                        description: Timestamp de quando a recomendação foi feita.
                                    similaridade:
                                        type: number
                                        description: O quão similar é o documento recomendado e os que serviram de base para a recomendação.
                                    aprovado: 
                                        type: boolean
                                        nullable: true
                                        description: Informa se o usuário aceitou ou não a recomendação.
                                    data_visualizacao: 
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
                            id_usuario:
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
                            id_recomendacao:
                                description: ID da recomendação a ser alterada.
                                type: string
                            aprovado:
                                description: booleando indicando se o usuário aprovou a recomendação. Caso não haja opinião, passar o campo em branco.
                                type: boolean
                                nullable: true
                            data_visualizacao:
                                description: Inteiro representando o timestamp de quando a recomendação foi vista. Se em branco, o próprio sistema preencherá o campo.
                                type:
                                    - int
                        required:
                            - id_recomendacao
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
                            id_recomendacao:
                                description: ID da recomendação a ser removida.
                                type: string
                        required:
                            - id_recomendacao      
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
    
    def _cosine_similarity(self, doc1, doc2):
        return np.dot(doc2, doc2)/(np.linalg.norm(doc1)*np.linalg.norm(doc2))
    
    def get(self, request):

        if 'id_usuario' in request.GET:
            user_id = request.GET['id_usuario']
            query = {'term': {'id_usuario.keyword': user_id}}
            _, reccomendations = DOC_REC.get_list(query, page='all')
            return Response(reccomendations, status=status.HTTP_200_OK)

        elif 'id_notificacao' in request.GET:
            notification_id = request.GET['id_notificacao']
            query = {'term': {'id_notificacao.keyword': notification_id}}
            _, reccomendations = DOC_REC.get_list(query, page='all')
            return Response(reccomendations, status=status.HTTP_200_OK) 

        elif 'id_recomendacao' in request.GET:
            rec_id = request.GET['id_recomendacao']
            reccomendation = DOC_REC.get(rec_id)
            if reccomendation is None:
                return Response({'message': 'A recomendação não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND) 
            return Response(reccomendation, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'É necessário informar pelo menos um dos campos: id_usuario, id_notificacao ou id_recomendacao.'})
    
    def post(self, request):
        id_usuario = request.POST.get('id_usuario', None)
        notification = Notification()

        if id_usuario == None or id_usuario == '':
            users_ids = DOC_REC.get_users_ids_to_recommend()

        else:
            users_ids = [id_usuario]

        # data da última recomendação de cada usuário
        user_dates = DOC_REC.get_last_recommendation_date()


        # quais os tipos de evidência que devem ser usadas na recomendação
        config_evidences, _ = self.config_rec_evidences.get(active=True)

        for id_usuario in users_ids:

            # usa como data de referência a data da última recomendação
            # se o usuário não possui data, usa a semana anterior como data de referência
            if id_usuario in user_dates:
                reference_date = user_dates[id_usuario]
                
            else:
                reference_date = '2021-04-01'

            # busca os documentos candidatos a recomendação
            candidates = DOC_REC.get_candidate_documents(reference_date)

            valid_recommendations = []

            for evidence_item in config_evidences:
                top_n = evidence_item['top_n_recommendations']
                min_similarity = evidence_item['min_similarity']

                # busca as evidências do(s) usuário(s)
                user_evidences = DOC_REC.get_evidences(id_usuario, evidence_item['evidence_type'], evidence_item['es_index_name'], evidence_item['amount'])

                # computa a similaridade entre os documentos candidatos e a evidência
                similarity_ranking = []

                evidence_ranking = dict()
                for evidence_i, evidence_doc in enumerate(user_evidences):
                    if evidence_i not in evidence_ranking:
                        evidence_ranking[evidence_i] = []

                    for candidate_i, candidate_doc in enumerate(candidates):
                        similarity_score = self._cosine_similarity(candidate_doc['embedding'], evidence_doc['embedding']) * 100
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
                            'id_usuario': id_usuario,
                            'id_notificacao': None,
                            'indice_doc_recomendado': candidates[candidate_i]['index_name'],
                            'id_doc_recomendado': candidates[candidate_i]['id'],
                            'recommended_doc_title': candidates[candidate_i]['title'],
                            'matched_from': evidence_item['evidence_type'],
                            'titulo_doc_recomendado': user_evidences[evidence_i]['query'],
                            'evidencia_indice_doc': user_evidences[evidence_i]['index_name'],
                            'evidencia_id_doc': user_evidences[evidence_i]['id'],
                            'evidencia_titulo_doc': user_evidences[evidence_i]['title'],
                            'data_criacao': int(time() * 1000),
                            'similaridade': score,
                            'aprovado': None
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
                    'id_usuario': id_usuario,
                    'message': 'Novos documentos que possam ser do seu interesse.',
                    'type': 'RECOMMENDATION',
                    'data_criacao': int(time() * 1000)
                })
                id_notificacao = notification_response['_id']

                for recommendation in valid_recommendations:
                    recommendation['id_notificacao'] = id_notificacao
                    DOC_REC.save(recommendation)


        return Response(status=status.HTTP_201_CREATED)
    
    def put(self, request):
        data = get_data_from_request(request.data)

        rec_id = data.get('id_recomendacao')
        if rec_id is None:
            return Response({'message': 'É necessário informar o campo id_recomendacao.'}, status=status.HTTP_400_BAD_REQUEST)

        rec = DOC_REC.get(rec_id)

        if rec is None:
            return Response({'message': 'A recomendação não existe ou não foi encontrada.'})

        del data['id_recomendacao']

        valid_fields = {'data_visualizacao', 'aprovado', 'visualizado'}
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        DOC_REC.parse_data_type(data)
        if DOC_REC.item_already_updated(rec, data):
            return Response({'message': 'A recomendação já está atualizado.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'visualizado' in data:
            data['data_visualizacao'] = get_current_timestamp() if str2bool(data['visualizado']) else None
            del data['visualizado']
            
        if DOC_REC.item_already_updated(rec, data):
            return Response({'message': 'A recomendação já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if DOC_REC.update(rec_id, data):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a recomendação, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self, request):
        data = get_data_from_request(request.data)

        if 'id_recomendacao' not in data:
            return Response({'message': 'Informe o ID da recomendação a ser deletada.'}, status.HTTP_400_BAD_REQUEST)
        
        rec_id = data['id_recomendacao']
        
        rec = DOC_REC.get(rec_id)
        if rec is None:
            return Response({'message': 'A recomendação não existe ou não foi encontrada.'}, status=status.HTTP_400_BAD_REQUEST) 

        if DOC_REC.delete(rec_id):
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Não foi possível remover a recomendação, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
