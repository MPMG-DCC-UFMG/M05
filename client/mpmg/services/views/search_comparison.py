import time

from django.conf import settings
from mpmg.services.models import SearchConfigs
from mpmg.services.query import Query
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

class CompareView(APIView):
    '''
    get:
      description: Realiza uma busca por documentos não estruturados comparando dois algoritmos diferentes. \
                   Os algoritmos são configurados na interface de administração da API.
      parameters:
        - name: api_client_name
          in: path
          description: Nome do cliente da API. Passe "procon" ou "gsi".
          required: true
          schema:
            type: string
        - name: query
          in: query
          description: texto da consulta
          required: true
          schema:
            type: string
        - name: page
          in: query
          description: Página do resultado de busca
          required: true
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: sid
          in: query
          description: ID da sessão do usuário na aplicação
          required: true
          schema:
            type: string
        - name: qid
          in: query
          description: ID da consulta. Quando _page=1_ passe vazio e este método irá cria-lo. \
                       Quando _page>1_ passe o qid retornado na primeira chamada.
          schema:
            type: string
        - name: instances
          in: query
          description: Filtro com uma lista de nomes de cidades às quais o documento deve pertencer
          schema:
            type: array
            items:
              type: string
        - name: doc_types
          in: query
          description: Filtro com uma lista de tipos de documentos que devem ser retornados
          schema:
            type: array
            items:
              type: string
              enum:
                - Diario
                - Processo
                - Licitacao
        - name: start_date
          in: query
          description: Filtra documentos cuja data de publicação seja igual ou posterior à data informada. Data no formato YYYY-MM-DD
          schema:
            type: string
        - name: end_date
          in: query
          description: Filtra documentos cuja data de publicação seja anterior à data informada. Data no formato YYYY-MM-DD
          schema:
            type: string
      responses:
        '200':
          description: Retorna uma lista com os documentos encontrados
          content:
            application/json:
              schema:
                type: object
                properties: {}
        '401':
          description: Requisição não autorizada caso não seja fornecido um token válido
    '''

    # permission_classes = (IsAuthenticated,)
    schema = AutoDocstringSchema()

    def get(self, request):
        # try:
        start = time.time()  # Medindo wall-clock time da requisição completa

        # try:
        self._generate_queries(request)

        if not self.regular_query.is_valid() or not self.replica_query.is_valid():
            data = {'error_type': 'invalid_query'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Busca os documentos no elastic com Algoritmo 1
        total_docs, total_pages, documents, response_time = self.regular_query.execute()

        # Busca os documentos no elastic com Algoritmo 2 (nos índices replica)
        total_docs_repl, total_pages_repl, documents_repl, response_time_repl = self.replica_query.execute()

        end = time.time()
        wall_time = end - start

        data = {
            'query': self.regular_query.query,
            'total_docs': total_docs,
            'time': wall_time,
            'response_time': response_time,
            'response_time_repl': response_time_repl,
            'results_per_page': self.regular_query.results_per_page,
            'current_page': self.regular_query.page,
            'total_pages': total_pages,
            'qid': self.regular_query.qid,  # TODO:sera retornado o qid de somente uma consulta
            'start_date': self.regular_query.start_date,
            'end_date': self.regular_query.end_date,
            'instances': self.regular_query.instances,
            'doc_types': self.regular_query.doc_types,
            'total_docs_repl': total_docs_repl,
            'total_pages_repl': total_pages_repl,
            # TODO: acertar isso para passar como parametro o grupo
            'algorithm_base': self.regular_query.algo_configs['type'],
            # TODO: acertar isso para passar como parametro o grupo
            'algorithm_repl': self.replica_query.algo_configs['type'],
            'documents': documents,
            'documents_repl': documents_repl,
        }
        return Response(data)

        # except:

        # except Exception as e:
        #     data = {
        #         'error_message': str(sys.exc_info())
        #     }
        #     print(sys.exc_info())
        #     return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_queries(self, request):
        # url parameters
        raw_query = request.GET['query']
        page = int(request.GET.get('page', 1))
        sid = request.GET['sid']
        qid = request.GET.get('qid', '')
        instances = request.GET.getlist('instances', [])
        doc_types = request.GET.getlist('doc_types', [])
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        user_id = request.user.id

        self.regular_query = Query(raw_query, page, qid, sid, user_id, instances,
                                   doc_types, start_date, end_date, use_entities=SearchConfigs.get_use_entities_in_search())

        self.replica_query = Query(raw_query, page, qid, sid, user_id, instances,
                                   doc_types, start_date, end_date, group='replica', use_entities=SearchConfigs.get_use_entities_in_search())  # TODO: Modificar o doc_types para incluir os indices do outro alg
