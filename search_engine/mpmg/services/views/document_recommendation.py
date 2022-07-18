from mpmg.services.models import DocumentRecommendation
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
            - name: api_client_name
              in: path
              description: Nome do cliente da API. Passe "procon" ou "gsi".
              required: true
              schema:
                type: string        
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
                                description: ID do usuário que receberá as recomendações. Passe "all" para recomendar para todos usuários.
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
                                description: Booleando indicando se o usuário aprovou a recomendação. Caso não haja opinião, passar o campo em branco.
                                type: boolean
                                nullable: true
                            visualizado:
                                description: Booleando informando se o usuário visualizou a recomendação. Se em branco, caso queira remover essa informação.
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
    
    def get(self, request, api_client_name):
        if 'id_recomendacao' in request.GET:
            rec_id = request.GET['id_recomendacao']
            reccomendation = DOC_REC.get(rec_id)
            if reccomendation is None:
                return Response({'message': 'A recomendação não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND) 
            return Response(reccomendation, status=status.HTTP_200_OK)

        elif 'id_notificacao' in request.GET:
            notification_id = request.GET['id_notificacao']
            query = {'term': {'id_notificacao.keyword': notification_id}}
            _, reccomendations = DOC_REC.get_list(query, page='all')
            return Response(reccomendations, status=status.HTTP_200_OK) 

        elif 'id_usuario' in request.GET:
            user_id = request.GET['id_usuario']
            query = {'term': {'id_usuario.keyword': user_id}}
            _, reccomendations = DOC_REC.get_list(query, page='all')
            return Response(reccomendations, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'É necessário informar pelo menos um dos campos: id_usuario, id_notificacao ou id_recomendacao.'})
    
    def post(self, request, api_client_name):
        user_id = request.POST.get('id_usuario')

        if user_id in (None, ''):
            user_id = 'all'

        else:

            # TODO: Checar se o ID passado pelo usuário é valido
            pass
        
        recommendations = DOC_REC.recommend(user_id, api_client_name) 
        return Response(recommendations, status=status.HTTP_201_CREATED)

    def put(self, request, api_client_name):
        data = get_data_from_request(request)

        rec_id = data.get('id_recomendacao')
        if rec_id is None:
            return Response({'message': 'É necessário informar o campo id_recomendacao.'}, status=status.HTTP_400_BAD_REQUEST)

        rec = DOC_REC.get(rec_id)

        if rec is None:
            return Response({'message': 'A recomendação não existe ou não foi encontrada.'})

        del data['id_recomendacao']

        valid_fields = {'aprovado', 'visualizado'}
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        update_visualized = False 
        mark_as_visualized = False 
    
        if 'visualizado' in data:
            update_visualized = True
            mark_as_visualized = str2bool(data['visualizado'])
            del data['visualizado']

        if mark_as_visualized and rec['data_visualizacao'] is not None:
            return Response({'message': 'A recomendação já foi visualizada.'}, status=status.HTTP_400_BAD_REQUEST)

        DOC_REC.parse_data_type(data)

        if update_visualized:
            data['data_visualizacao'] = get_current_timestamp() if mark_as_visualized else None
        
        if DOC_REC.item_already_updated(rec, data):
            return Response({'message': 'A recomendação já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if DOC_REC.update(rec_id, data):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a recomendação, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self, request, api_client_name):
        data = get_data_from_request(request)

        if 'id_recomendacao' not in data:
            return Response({'message': 'Informe o ID da recomendação a ser deletada.'}, status.HTTP_400_BAD_REQUEST)
        
        rec_id = data['id_recomendacao']
        
        rec = DOC_REC.get(rec_id)
        if rec is None:
            return Response({'message': 'A recomendação não existe ou não foi encontrada.'}, status=status.HTTP_400_BAD_REQUEST) 

        if DOC_REC.delete(rec_id):
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Não foi possível remover a recomendação, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
