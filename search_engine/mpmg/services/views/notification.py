from time import time

from mpmg.services.models import Notification
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

class NotificationView(APIView):

    '''
    get:
        description: Retorna uma lista de notificações de de um usuário se o ID dele for informado ou uma notificação específica, se o id dela for passado.
        parameters:
            - name: id_usuario
              in: query
              description: ID do usuário
              required: true
              schema:
                    type: string
            - name: id_notificacao
              in: query
              description: ID da notificação a ser recuperada.
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna uma notifição ou uma lista dela.
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: ID da notificação.
                                    id_usuario:
                                        type: string
                                        description: ID do usário a quem a notificação se destina.
                                    texto:
                                        type: string
                                        description: Texto da notificação.
                                    tipo:
                                        type: string
                                        description: Tipo da notificação, por enquanto, somente "RECOMMENDATION".
                                    data_criacao:
                                        type: integer
                                        description: Timestamp de quando a notificação foi criada.
                                    data_visualizacao:
                                        type: integer
                                        description: Timestamp de quando a notificação foi vista.
                                        nullable: true
    post:
        description: Cria uma notificação.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_usuario:
                                description: ID do usuário a quem se destina a notificação.
                                type: string
                            texto:
                                description: Texto da notificação.
                                type: string
                            tipo:
                                description: Informa o tipo da notificação.
                                type: string
                        required:
                            - id_usuario
                            - texto
                            - tipo
        responses:
            '201':
                description: A notificação foi criada com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_notificacao: 
                                    type: string
                                    description: ID da notificação crida.
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

    put:
        description: Atualiza a data de visualização de uma notificação específica.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_notificacao:
                                description: ID da notificação a ser alterada.
                                type: string
                            data_visualizacao:
                                description: Timestamp da visualização da notificação. Se não for informado, o sistema obterá automaticamente com base no tempo atual.
                                type: string
                        required:
                            - id_notificacao
        responses:
            '204':
                description: As alterações foram executadas com sucesso.
            '400':
                description: O ID da notificação não foi informado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
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
    delete:
        description: Apaga uma notificação.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_notificacao:
                                description: ID da notificação a ser removida.
                                type: string
                        required:
                            - id_notificacao      
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

    def get(self, request):
        id_usuario = request.GET.get('id_usuario')
        id_notificacao = request.GET.get('id_notificacao')

        if id_usuario is None and id_notificacao is None:
            return Response({'message': 'Informe o campo id_usuario ou id_notificacao!'}, status=status.HTTP_400_BAD_REQUEST)

        if id_notificacao:
            notification = Notification().get_by_id(id_notificacao)
            if notification is None:
                return Response({'message': 'Verifique se o ID da notificação informado é válido!'}, status=status.HTTP_404_NOT_FOUND)
            return Response(notification, status=status.HTTP_200_OK)

        if id_usuario:
            notifications_list = Notification().get_by_user(id_usuario=id_usuario)
            return Response(notifications_list, status=status.HTTP_200_OK)

    def post(self, request):
        id_notificacao, msg_error = Notification().save(dict(
            id_usuario=request.POST['id_usuario'],
            texto=request.POST['texto'],
            tipo=request.POST['tipo'],
            data_criacao=int(time() * 1000),
            data_visualizacao=None,
        ))

        if id_notificacao:
            return Response({'id_notificacao': id_notificacao}, status=status.HTTP_201_CREATED)

        return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        data = request.data.dict()

        id_notificacao = data.get('id_notificacao')
        if id_notificacao is None:
            return Response({'message': 'Informe o ID da notificação visualizada.'}, status.HTTP_400_BAD_REQUEST)

        data_visualizacao = data.get('data_visualizacao', '')

        if data_visualizacao == '':
            # FIXME: Usar um método padronizado para obter o timestamp
            data_visualizacao = int(time() * 1000)

        success, msg_error = Notification().mark_as_visualized(
            id_notificacao, data_visualizacao)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = request.data.dict()

        id_notificacao = data.get('id_notificacao')
        if id_notificacao is None:
            return Response({'message': 'Informe o ID da notificação deletada.'}, status.HTTP_400_BAD_REQUEST)

        success, msg_error = Notification().remove(id_notificacao)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)
