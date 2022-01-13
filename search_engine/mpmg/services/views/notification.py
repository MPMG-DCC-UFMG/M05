from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import Notification


class NotificationView(APIView):
    '''
    get:
        description: Retorna uma lista de notificações de de um usuário.
        parameters:
            - name: user_id
              in: query
              description: ID do usuário
              required: true
              schema:
                    type: string
    
    post:
        description: bla bla bla
    
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
                                description: Data da visualização no formato Y-m-d. Se não for informado será usada a data corrente.
                                type: string
                        required:
                            - notification_id
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.

    '''
    
    schema = AutoDocstringSchema()


    def get(self, request):
        user_id = request.GET['user_id']
        
        notifications_list = Notification().get_by_user(user_id=user_id)
        
        return Response(notifications_list, status=status.HTTP_200_OK)
    

    def post(self, request):
        return Response({})


    def put(self, request):
        notification_id = request.POST['notification_id']
        date_visualized = request.POST.get('date_visualized', '') 
        
        if date_visualized == '':
            date_visualized = datetime.now().timestamp()

        success, msg_error = Notification().mark_as_visualized(notification_id, date_visualized)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_400_BAD_REQUEST)




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