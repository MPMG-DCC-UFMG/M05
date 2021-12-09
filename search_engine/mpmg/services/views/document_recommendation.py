from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import DocumentRecomendation


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
        description: bla bla bla
    
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

    
    def get(self, request):
        user_id = request.GET['user_id']
        
        recommendations_list = DocumentRecomendation().get_by_user(user_id=user_id)
        
        return Response(recommendations_list, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        return Response({})
    

    def put(self, request):
        recommendation_id = request.POST['recommendation_id']
        accepted = request.POST['accepted']

        success, msg_error = DocumentRecomendation().update(recommendation_id, accepted)
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