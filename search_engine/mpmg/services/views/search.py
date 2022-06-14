import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..docstring_schema import AutoDocstringSchema
from ..elastic import Elastic
from ..query import Query
from ..query_filter import QueryFilter
from ..reranker import Reranker


class SearchView(APIView):
    '''
    get:
        description: Realiza uma busca por documentos não estruturados
        parameters:
            -   name: consulta
                in: query
                description: texto da consulta
                required: true
                schema:
                    type: string
            -   name: pagina
                in: query
                description: Página do resultado de busca
                required: true
                schema:
                    type: integer
                    minimum: 1
                    default: 1
            -   name: sid
                in: query
                description: ID da sessão do usuário na aplicação
                required: true
                schema:
                    type: string
            -   name: qid
                in: query
                description: ID da consulta. Quando _page=1_ passe vazio e este método irá cria-lo. \
                            Quando _page>1_ passe o qid retornado na primeira chamada.
                schema:
                    type: string
            -   name: filtro_instancias
                in: query
                description: Filtro com uma lista de nomes de cidades às quais o documento deve pertencer
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_tipos_documentos
                in: query
                description: Filtro com uma lista de tipos de documentos que devem ser retornados
                schema:
                    type: array
                    items:
                        type: string
                        enum:
                            - diarios
                            - processos
                            - licitacoes
                            - diarios_segmentado
            -   name: filtro_data_inicio
                in: query
                description: Filtra documentos cuja data de publicação seja igual ou posterior à data informada. Data no formato YYYY-MM-DD
                schema:
                    type: string
            -   name: filtro_data_fim
                in: query
                description: Filtra documentos cuja data de publicação seja anterior à data informada. Data no formato YYYY-MM-DD
                schema:
                    type: string
            -   name: filtro_entidade_pessoa
                in: query
                description: Filtra documentos que mencionem as pessoas informadas nesta lista, além dos termos da consulta
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_entidade_municipio
                in: query
                description: Filtra documentos que mencionem os municípios informados nesta lista, além dos termos da consulta
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_entidade_organizacao
                in: query
                description: Filtra documentos que mencionem as organizações informadas nesta lista, além dos termos da consulta
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_entidade_local
                in: query
                description: Filtra documentos que mencionem os locais informados nesta lista, além dos termos da consulta
                schema:
                    type: array
                    items:
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
    reranker = Reranker()

    def get(self, request, api_client_name):
        start = time.time()  # Medindo wall-clock time da requisição completa

        # try:
        self.elastic = Elastic()
        self._generate_query(request, api_client_name)

        # valida o tamanho da consulta
        if not self.query.is_valid():
            data = {'error_type': 'invalid_query'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Busca os documentos no elastic
        total_docs, total_pages, documents, response_time = self.query.execute()

        # reranking goes here
        documents = self.reranker.rerank(request.GET['consulta'], documents)

        end = time.time()
        wall_time = end - start

        data = {
            'time': wall_time,
            'time_elastic': response_time,
            'consulta': self.query.query,
            'qid': self.query.qid,
            'resultados_por_pagina': self.query.results_per_page,
            'pagina_atual': self.query.page,
            'documentos': documents,
            'total_documentos': total_docs,
            'total_paginas': total_pages,
            'filtro_data_inicio': self.query.query_filter.start_date,
            'filtro_data_fim': self.query.query_filter.end_date,
            'filtro_instancias': self.query.query_filter.instances,
            'filtro_tipos_documentos': self.query.query_filter.doc_types,
        }
        return Response(data)

    def _generate_query(self, request, api_client_name):
        group = 'regular'
        user_id = request.user.id
        raw_query = request.GET['consulta']
        page = int(request.GET.get('pagina', 1))
        sid = request.GET['sid']
        qid = request.GET.get('qid', '')

        # o eostante dos parâmetros do request são lidos automaticamente
        query_filter = QueryFilter.create_from_request(request)

        self.query = Query(raw_query, page, qid, sid,
                           user_id, api_client_name, group, query_filter=query_filter)
