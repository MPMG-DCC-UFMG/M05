from time import time 
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import Notification


class NotificationView(APIView):

    '''
    get:
        description: Retorna uma lista de notificações de de um usuário se o ID dele for informado ou uma notificação específica, se o id dela for passado.
        parameters:
            - name: user_id
              in: query
              description: ID do usuário
              required: true
              schema:
                    type: string
            - name: notification_id
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
                                    user_id:
                                        type: string
                                        description: ID do usário a quem a notificação se destina.
                                    message:
                                        type: string
                                        description: Texto da notificação.
                                    type:
                                        type: string
                                        description: Tipo da notificação, por enquanto, somente "RECOMMENDATION".
                                    date:
                                        type: integer
                                        description: Timestamp de quando a notificação foi criada.
                                    date_visualized:
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
                            user_id:
                                description: ID do usuário a quem se destina a notificação.
                                type: string
                            message:
                                description: Texto da notificação.
                                type: string
                            type:
                                description: Informa o tipo da notificação.
                                type: string
                        required:
                            - user_id
                            - message
                            - type
        responses:
            '201':
                description: A notificação foi criada com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                notification_id: 
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
                            notification_id:
                                description: ID da notificação a ser alterada.
                                type: string
                            date_visualized:
                                description: Timestamp da visualização da notificação. Se não for informado, o sistema obterá automaticamente com base no tempo atual.
                                type: string
                        required:
                            - notification_id
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
                            notification_id:
                                description: ID da notificação a ser removida.
                                type: string
                        required:
                            - notification_id      
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
        user_id = request.GET.get('user_id')
        notification_id = request.GET.get('notification_id')

        if user_id is None and notification_id is None:
            return Response({'message': 'Informe o campo user_id ou notification_id!'}, status=status.HTTP_400_BAD_REQUEST)

        if notification_id:
            notification = Notification().get_by_id(notification_id)
            if notification is None:
                return Response({'message': 'Verifique se o ID da notificação informado é válido!'}, status=status.HTTP_404_NOT_FOUND)
            return Response(notification, status=status.HTTP_200_OK)

        if user_id:
            notifications_list = Notification().get_by_user(user_id=user_id)
            return Response(notifications_list, status=status.HTTP_200_OK)

    def post(self, request):
        notification_id, msg_error = Notification().save(dict(
            user_id = request.POST['user_id'],
            message = request.POST['message'],
            type = request.POST['type'],
            date = int(time() * 1000),
            date_visualized = None,
        ))

        if notification_id:
            return Response({'notification_id': notification_id}, status=status.HTTP_201_CREATED)
        
        return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request):
        data = request.data.dict()

        notification_id = data.get('notification_id')
        if notification_id is None:
            return Response({'message': 'Informe o ID da notificação visualizada.'}, status.HTTP_400_BAD_REQUEST)
        
        date_visualized = data.get('date_visualized', '') 
        
        if date_visualized == '':
            # ElasticSearch precisa que o timestamp seja em milisegundos
            date_visualized = int(time() * 1000)

        success, msg_error = Notification().mark_as_visualized(notification_id, date_visualized)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = request.data.dict()

        notification_id = data.get('notification_id')
        if notification_id is None:
            return Response({'message': 'Informe o ID da notificação deletada.'}, status.HTTP_400_BAD_REQUEST)
        
        success, msg_error = Notification().remove(notification_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddFakeNotificationsView():
    '''
    CLASSE TEMPORÁRIA que adiciona notificações para um determinado usuário
    para a execução de testes. Remova-a quando não for mais necessário
    
    Para executá-la siga os passos abaixo:

    1. Entre no shell do django: 
        python manage.py shell
    
    2. Execute:
        from mpmg.services.views.notification import AddFakeNotificationsView
        AddFakeNotificationsView().execute(1) # 1 é o user_id, altere de acordo
    '''

    def execute(self, user_id):
        from ..elastic import Elastic
        elastic = Elastic()
        
        # antes de inserir, deleta as existentes
        search_obj = elastic.dsl.Search(using=elastic.es, index='notifications')
        search_obj = search_obj.query(elastic.dsl.Q({"term": { "user_id": user_id }}))
        search_obj.delete()

        
        # insere 5 novas notificações
        for i in range(5):
            body = {
                'user_id': user_id,
                'message': 'Texto da notificação '+str(i+1),
                'type': 'DOC_RECOMMENDATION',
                'date': '2021-0'+str(i+1)+'-01',
                'date_visualized': None if i in [3,4] else '2021-0'+str(i+1)+'-02',
            }
            elastic.es.index(index='notifications', body=body)