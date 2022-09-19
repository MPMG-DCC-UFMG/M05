import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..docstring_schema import AutoDocstringSchema
from ..elastic import Elastic
from ..query import Query
from ..query_filter import QueryFilter
from ..reranker import Reranker

SORT_BY_RELEVANCE = 'relevancia'
SORT_BY_DATE = 'data'

SORT_ORDER_DESC = 'descendente'
SORT_ORDER_ASC = 'ascendente'

SORT_ORDER_DESC_SHORT = 'desc'
SORT_ORDER_ASC_SHORT = 'asc'

class SearchView(APIView):
    '''
    get:
        description: Realiza uma busca por documentos não estruturados
        parameters:
            -   name: api_client_name
                in: path
                description: Nome do cliente da API. Passe "procon" ou "gsi".
                required: true
                schema:
                    type: string
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
            -   name: tipo_ordenacao
                in: query
                description: Tipo da ordenação dos documentos. Caso queira que os documentos retornados para \
                            a consulta sejam ordenados por relevância, passe "relevancia" (sem aspas). Já caso \
                            queira que seja ordenado por data, passe "data" (sem aspas). Caso nenhum for passado, \
                            o default é ordenação por relevância.
                schema:
                    type: string
                    enum:
                        - relevancia
                        - data
            -   name: ordenacao
                in: query
                description: Recebe asc ou desc para, caso tipo_ordenacao receba "data" (sem aspas), o sistema ordenará os \
                        documentos por data em ordem ascendente ou descendente, respectivamente. É possível passar o nome \
                        completo, ascendente ou descendente, com igual semântica.
                schema:
                    type: string
                    enum:
                        - asc
                        - ascendente
                        - desc
                        - descendente
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
            -   name: filtro_estado
                in: query
                description: Filtra documentos pela sigla de um estado do Brasil (case-insensitive), além dos termos da consulta.
                schema:
                    type: string
            -   name: filtro_cidade
                in: query
                description: Filtra documentos de uma cidade do Brasil (case-insensitive), além dos termos da consulta.
                schema:
                    type: string
            -   name: filtro_categoria_empresa
                in: query
                description: Filtra documentos que contém categorias de empresas informados nesta lista, alémd dos termos da consulta
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
                            properties: 
                                doc_counts_by_index: 
                                    type: object
                                    description: Dicionário com número de documentos encontrados para pesquisa por índice.
                                doc_counts_by_category: 
                                    type: object
                                    description: Dicionário com número de documentos encontrados para pesquisa por categoria.
                                doc_counts_by_company_category: 
                                    type: object
                                    description: Dicionário com número de documentos encontrados para pesquisa por categoria de empresa.
                                time:
                                    type: number
                                    description: Tempo de execução total.
                                time_elastic:
                                    type: number
                                    description: Tempo de execução da consulta pelo Elastic Search.
                                consulta:
                                    type: string
                                    description: Consulta que originou a busca.
                                qid:
                                    type: string
                                    description: ID da consulta.
                                resultados_por_pagina:
                                    type: integer
                                    description: Número de resultados por página.
                                pagina_atual:
                                    type: string
                                    description: Número da página atual.
                                documentos:
                                    type: array
                                    description: Lista de documentos ordenados por relevância para a consulta.
                                    schema:
                                        items:
                                            type: object
                                total_paginas:
                                    type: string
                                    description: Número de páginas que o resultado da busca foi paginado.
                                filtro_data_inicio:
                                    type: string
                                    description: Texto correspondente ao filtro por data de início.
                                filtro_data_fim:
                                    type: string
                                    description: Texto correspondente ao filtro por data final.
                                filtro_instancias:
                                    type: string
                                    description: .
                                filtro_tipos_documentos:
                                    type: array
                                    description: Filtro com uma lista de tipos de documentos que devem ser retornados
                                    schema:
                                        items:
                                            type: string
                                            enum:
                                                - diarios
                                                - processos
                                                - licitacoes
                                                - diarios_segmentado
                                filtro_categoria_empresa:
                                    type: array
                                    description: Lista com strings utilizados na filtragem por categorias de empresa.
                                    schema:
                                        items:
                                            type: string
                                filtro_cidade:
                                    type: string
                                    description: Texto correspondente ao filtro de cidade.
                                filtro_estado:
                                    type: string
                                    description: Texto correspondende ao filtro de estado.
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
        total_docs, total_pages, documents, response_time, doc_counts_by_index, doc_counts_by_category, doc_counts_by_company_category = self.query.execute()

        # # reranking goes here

        if self.query.sort_by == SORT_BY_RELEVANCE:
            documents = self.reranker.rerank(request.GET['consulta'], documents)
        
        end = time.time()
        wall_time = end - start

        data = {
            'doc_counts_by_index': doc_counts_by_index,
            'doc_counts_by_category': doc_counts_by_category,
            'doc_counts_by_company_category': doc_counts_by_company_category,
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
            'filtro_categoria_empresa': self.query.query_filter.business_categories_filter,
            'filtro_cidade': self.query.query_filter.location_filter.get('cidade'),
            'filtro_estado': self.query.query_filter.location_filter.get('sigla_estado')
        }

        return Response(data)

    def _generate_query(self, request, api_client_name):
        group = 'regular'
        user_id = request.user.id
        raw_query = request.GET['consulta']
        page = int(request.GET.get('pagina', 1))
        sid = request.GET['sid']
        qid = request.GET.get('qid', '')

        sort_by = request.GET.get('tipo_ordenacao', SORT_BY_RELEVANCE).lower()
        sort_order = request.GET.get('ordenacao', SORT_ORDER_DESC).lower()

        if sort_by not in (SORT_BY_RELEVANCE, SORT_BY_DATE):
            sort_by = SORT_BY_RELEVANCE

        if sort_order not in (SORT_ORDER_ASC, SORT_ORDER_ASC_SHORT, SORT_ORDER_DESC, SORT_ORDER_DESC_SHORT):
            sort_order = SORT_ORDER_DESC_SHORT

        if sort_order == SORT_ORDER_DESC:
            sort_order = SORT_ORDER_DESC_SHORT
        
        elif sort_order == SORT_ORDER_ASC:
            sort_order = SORT_ORDER_ASC_SHORT

        # o eostante dos parâmetros do request são lidos automaticamente
        query_filter = QueryFilter.create_from_request(request, api_client_name)
        self.query = Query(raw_query, page, qid, sid, user_id, sort_by, sort_order, 
                            api_client_name, group, query_filter=query_filter)
