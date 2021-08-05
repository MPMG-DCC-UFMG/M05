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
from ..features_extractor import FeaturesExtractor
from ..ranking.tf_idf import TF_IDF
from ..features_extractor import TermVectorsFeaturesExtractor
from ..query import Query
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
        start = time.time() # Medindo wall-clock time da requisição completa

        # try:
        self.elastic = Elastic()
        self._generate_query(request)

            # valida o tamanho da consulta
        if not self.query.is_valid():
            # print("query invalida")
            data = {'error_type': 'invalid_query'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        # Busca os documentos no elastic
        total_docs, total_pages, documents, response_time, entities_filter_list = self.query.execute()

        end = time.time()
        wall_time = end - start
        
        data = {
            'query': self.query.query,
            'current_page': self.query.page,
            'qid': self.query.qid,
            'total_docs': total_docs,
            'total_pages': total_pages,
            'results_per_page': self.query.results_per_page,
            'time': wall_time,
            'time_elastic': response_time,
            'start_date': self.query.start_date,
            'end_date': self.query.end_date,
            'instances': self.query.instances,
            'doc_types': self.query.doc_types,
            'documents': documents,
            'entities_filter_list': entities_filter_list,
        }               
        return Response(data)
        
        # except Exception as e:
        #     data = {
        #         'error_message': str(sys.exc_info())
        #     }
        #     print(sys.exc_info())
        #     return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def _generate_query(self, request):
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
        
        entidade_pessoa_filter = request.GET.getlist('entidade_pessoa_filter', [])
        entidade_municipio_filter = request.GET.getlist('entidade_municipio_filter', [])
        entidade_organizacao_filter = request.GET.getlist('entidade_organizacao_filter', [])
        entidade_local_filter = request.GET.getlist('entidade_local_filter', [])
        entity_filter = {}
        if len(entidade_pessoa_filter) > 0:
          entity_filter['entidade_pessoa'] = entidade_pessoa_filter
        if len(entidade_municipio_filter) > 0:
          entity_filter['entidade_municipio'] = entidade_municipio_filter
        if len(entidade_organizacao_filter) > 0:
          entity_filter['entidade_organizacao'] = entidade_organizacao_filter
        if len(entidade_local_filter) > 0:
          entity_filter['entidade_local'] = entidade_local_filter

        self.query = Query(raw_query, page, qid, sid, user_id, instances, 
                doc_types, start_date, end_date, use_entities=SearchConfigs.get_use_entities_in_search(), entity_filter=entity_filter)



        

    

    