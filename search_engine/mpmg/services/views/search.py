import sys
import time

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from mpmg.services.models import LogSearch, Document
from mpmg.services.models import SearchConfigs
from ..elastic import Elastic
from ..reranker import Reranker
from ..features_extractor import FeaturesExtractor
from ..ranking.tf_idf import TF_IDF
from ..features_extractor import TermVectorsFeaturesExtractor
from ..query import Query
from ..query_filter import QueryFilter
from ..docstring_schema import AutoDocstringSchema



class SearchView(APIView):
    '''
    get:
      description: Realiza uma busca por documentos não estruturados
      parameters:
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
        - name: filter_instances
          in: query
          description: Filtro com uma lista de nomes de cidades às quais o documento deve pertencer
          schema:
            type: array
            items:
              type: string
        - name: filter_doc_types
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
        - name: filter_start_date
          in: query
          description: Filtra documentos cuja data de publicação seja igual ou posterior à data informada. Data no formato YYYY-MM-DD
          schema:
            type: string
        - name: filter_end_date
          in: query
          description: Filtra documentos cuja data de publicação seja anterior à data informada. Data no formato YYYY-MM-DD
          schema:
            type: string
        - name: filter_entidade_pessoa
          in: query
          description: Filtra documentos que mencionem as pessoas informadas nesta lista, além dos termos da consulta
          schema:
            type: array
            items:
              type: string
        - name: filter_entidade_municipio
          in: query
          description: Filtra documentos que mencionem os municípios informados nesta lista, além dos termos da consulta
          schema:
            type: array
            items:
              type: string
        - name: filter_entidade_organizacao
          in: query
          description: Filtra documentos que mencionem as organizações informadas nesta lista, além dos termos da consulta
          schema:
            type: array
            items:
              type: string
        - name: filter_entidade_local
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
    
    def get(self, request):
        start = time.time() # Medindo wall-clock time da requisição completa

        # try:
        self.elastic = Elastic()
        self._generate_query(request)


        # valida o tamanho da consulta
        if not self.query.is_valid():
            data = {'error_type': 'invalid_query'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        # Busca os documentos no elastic
        total_docs, total_pages, documents, response_time = self.query.execute()

        # reranking goes here
        documents = self.reranker.rerank(request.GET['query'], documents)

        end = time.time()
        wall_time = end - start
        
        data = {
            'time': wall_time,
            'time_elastic': response_time,
            'query': self.query.query,
            'qid': self.query.qid,
            'results_per_page': self.query.results_per_page,
            'current_page': self.query.page,
            'documents': documents,
            'total_docs': total_docs,
            'total_pages': total_pages,
            'filter_start_date': self.query.query_filter.start_date,
            'filter_end_date': self.query.query_filter.end_date,
            'filter_instances': self.query.query_filter.instances,
            'filter_doc_types': self.query.query_filter.doc_types,
        }               
        return Response(data)
        
        # except Exception as e:
        #     data = {
        #         'error_message': str(sys.exc_info())
        #     }
        #     print(sys.exc_info())
        #     return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def _generate_query(self, request):
        group = 'regular'
        user_id = request.user.id
        raw_query = request.GET['query']
        page = int(request.GET.get('page', 1))
        sid = request.GET['sid']
        qid = request.GET.get('qid', '')
        
        # o restante dos parâmetros do request são lidos automaticamente
        query_filter = QueryFilter.create_from_request(request)

        self.query = Query(raw_query, page, qid, sid, user_id, group, query_filter=query_filter)



        

    

    