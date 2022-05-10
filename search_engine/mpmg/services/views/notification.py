from time import time

from mpmg.services.models import Notification, notification
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators, get_data_from_request, get_current_timestamp, str2bool 

# FIXME: Fazer com que os métodos de Notification sejam estáticos para não precisar criar novas instâncias a todo momento, o mesmo para outro modelos
NOTIFICATION = Notification()

class NotificationView(APIView):

    '''
    get:
        description: Retorna uma lista de notificações de um usuário se o ID dele for informado ou uma notificação específica, se o ID dela for passado.
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
            '400':
                description: Não foi informado o id_usuario nem id_notificacao, necessários para obter a notificação.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404': 
                description: A notificação não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem informando que a notificação não foi encontrada.

    post:
        description: Cria uma notificação e retorna seu ID.
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
            '400':
                description: Algum(ns) do(s) campo(s) de criação foi(ram) informado(s) incorretamente.
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

    put:
        description: Atualiza os campos de uma notificação. Os campos disponíveis para atualização são: visualizado, texto e tipo.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_notificacao:
                                description: ID da notificação a ser alterada.
                                type: string
                            visualizado:
                                description: Informa se a notificação foi visualizada ou não. É possível enviar null para remover a informação de que se foi visualizado ou não.
                                type: boolean
                            texto:
                                description: Texto da notificação.
                                type: boolean
                            tipo:
                                description: Tipo da notificação.
                                type: boolean
                        required:
                            - id_notificacao
        responses:
            '204':
                description: As alterações foram executadas com sucesso.
            '400':
                description: O ID da notificação não foi informado e/ou algum(s) campo(s) foram passados incorretamente.
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
            '400':
                description: O ID da notificação não foi informado ou a notificação não existe.
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

    '''

    schema = AutoDocstringSchema()

    def get(self, request):
        id_usuario = request.GET.get('id_usuario')
        id_notificacao = request.GET.get('id_notificacao')
        
        if id_notificacao:
            notification = NOTIFICATION.get(id_notificacao)
            if notification is None:
                return Response({'message': 'Verifique se o ID da notificação informado é válido!'}, status=status.HTTP_404_NOT_FOUND)
            return Response(notification, status=status.HTTP_200_OK)

        elif id_usuario:
            query = {'term': {'id_usuario.keyword': id_usuario}}
            sort = {'data_criacao': {'order': 'desc'}}

            _, notifications = NOTIFICATION.get_list(query, page='all', sort=sort)

            return Response(notifications, status=status.HTTP_200_OK)
        
        else:
            return Response({'message': 'Informe o campo id_usuario ou id_notificacao!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        data = get_data_from_request(request)

        expected_fields = {'id_usuario', 'texto', 'tipo'}    
        optional_fields = {'data_visualizacao'}

        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields, optional_fields)
        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)
        
        NOTIFICATION.parse_data_type(data)
        id_notificacao = NOTIFICATION.save(dict(
            id_usuario=data['id_usuario'],
            texto=data['texto'],
            tipo=data['tipo'],
            data_visualizacao=data.get('data_visualizacao'),
        ))

        if id_notificacao:
            return Response({'id_notificacao': id_notificacao}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Não foi possível criar a notificação, tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        data = get_data_from_request(request)
        
        notification_id = data.get('id_notificacao')
        if notification_id is None:
            return Response({'message': 'Informe o ID da notificação a ser editada.'}, status.HTTP_400_BAD_REQUEST)
        del data['id_notificacao']
        
        notification = NOTIFICATION.get(notification_id)

        if notification is None:
            return Response({'message': 'A notificação não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # campos que o usuário pode editar
        valid_fields = {'texto', 'tipo', 'visualizado'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)


        update_visualized = False 
        mark_as_visualized = False 
    
        if 'visualizado' in data:
            update_visualized = True
            mark_as_visualized = str2bool(data['visualizado'])
            del data['visualizado']

        if mark_as_visualized and notification['data_visualizacao'] is not None:
            return Response({'message': 'A notificação já foi visualizada.'}, status=status.HTTP_400_BAD_REQUEST)

        NOTIFICATION.parse_data_type(data)
        
        if update_visualized:
            data['data_visualizacao'] = get_current_timestamp() if mark_as_visualized else None

        if NOTIFICATION.item_already_updated(notification, data):
            return Response({'message': 'A notificação já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)
        
        success = NOTIFICATION.update(notification_id, data)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a notificação, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = get_data_from_request(request)

        try:
            notification_id = data['id_notificacao']
        
        except KeyError:
            return Response({'message': 'Informe o ID da notificação a ser deletada.'}, status.HTTP_400_BAD_REQUEST)

        notification = NOTIFICATION.get(notification_id)
        if notification is None:
           return Response({'message': 'A notificação não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        success = NOTIFICATION.delete(notification_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível remover a notificação, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)