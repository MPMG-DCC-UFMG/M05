import math
from collections import defaultdict
from traceback import print_tb

from mpmg.services.models import (APIConfig, ConfigFilterByEntity,
                                  ConfigRankingEntity)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ..docstring_schema import AutoDocstringSchema
from ..elastic import Elastic
from ..query_filter import QueryFilter

CONFIG_FILTER_BY_ENTITY = ConfigFilterByEntity()
CONFIG_RANKING_ENTITY = ConfigRankingEntity()

class SearchEntities(APIView):
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
        -   name: uso
            in: path
            description: A que se destina as entidades retornadas, pode ser para geração de filtros ou ranking de entidades.
            required: true
            schema:
                type: string
                enum:
                    - filtro
                    - ranking
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
            description: Retorna um objeto com as entidades relacionadas.
            content:
                application/json:
                    schema:
                        type: object
                        properties: {}
        '400':
            description: Não foi informado os campos obrigatórios de forma válida.
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

    def get(self, request, api_client_name):
        usage_objective = request.GET.get('uso', '').lower()

        if usage_objective not in ('filtro', 'ranking'):
            return Response({'message': 'É necessário informar o objetivo de uso das entidades, que pode ser `filtro` ou `ranking`.'}, status=status.HTTP_400_BAD_REQUEST)

        if usage_objective == 'ranking':
            # buscamos todas as configs de ranking de entidades mas que estejam ativas
            _, config_entities_ranking = CONFIG_RANKING_ENTITY.get_list(page='all', filter=[{'term': {'ativo': True}}, {'term': {'nome_cliente_api': api_client_name}}])
            entities_by_entity_type = self._get_entities(request, config_entities_ranking, 'tamanho_ranking')

            entities_ranking_by_entity_type = dict()
            for config_entity_ranking in config_entities_ranking:
                name = config_entity_ranking['nome']
                entity_type = config_entity_ranking['tipo_entidade']
 
                entities_ranking_by_entity_type[entity_type] = {
                    'ranking': entities_by_entity_type[entity_type],
                    'nome': name
                } 
            
            data = entities_ranking_by_entity_type

        else:
            # buscamos todas as configs de ranking de entidades mas que estejam ativas
            _, config_filter_by_entity = CONFIG_FILTER_BY_ENTITY.get_list(page='all', filter=[{'term': {'ativo': True}}, {'term': {'nome_cliente_api': api_client_name}}])
            data = self._get_entities(request, config_filter_by_entity, 'num_entidades')

        return Response(data, status=status.HTTP_200_OK)

    def _aggregate_strategies(self, total, score, strategy):
        if strategy == "votes":
            return 1

        if strategy == "combsum":
            return score
        
        if strategy == "expcombsum":
            return math.exp(score)
        
        if strategy == "max":
            return max(total, score)

    def _aggregate_scores(self, response, entity_types: list, aggregation_strategy_by_entity_type: list):
        entities = {}
        for t in entity_types:
            entities[t] = defaultdict(int)

        for doc in response:
            for entity_field, aggregation_strategy in zip(entity_types, aggregation_strategy_by_entity_type):
                try:
                   entities_list = eval(doc[entity_field])
                
                except:
                    entities_list = []

                for ent in entities_list:
                    entities[entity_field][ent.lower()] += \
                        self._aggregate_strategies(
                            entities[entity_field][ent.lower()],
                            doc.meta.score,
                            aggregation_strategy
                        )
        return entities

    def _get_entities(self, request, config: list, num_entities_field: str):
        query = request.GET['consulta']

        query_filter = QueryFilter.create_from_request(request)

        entity_types = [] 
        aggregation_strategy_by_entity_type = []
        num_entities_by_entity_type = []

        for config_entity in config:
            entity_types.append(config_entity['tipo_entidade'])
            aggregation_strategy_by_entity_type.append(config_entity['tecnica_agregacao'])
            num_entities_by_entity_type.append(config_entity[num_entities_field])

        elastic = Elastic()

        indices = APIConfig.searchable_indices('regular')
        if len(query_filter.doc_types) > 0:
            indices = query_filter.doc_types

        must_clause = [elastic.dsl.Q('query_string', query=query, fields=APIConfig.searchable_fields())]
        filter_clause = query_filter.get_filters_clause()

        elastic_request = elastic.dsl.Search(using=elastic.es, index=indices) \
                        .source(entity_types) \
                        .query("bool", must = must_clause, should = [], filter = filter_clause)

        response = elastic_request.execute()
        entities =  self._aggregate_scores(response, entity_types, aggregation_strategy_by_entity_type)
   
        # pegas as num_entities entidades que mais aparecem
        selected_entities = {}
        for entity_field, num_entities in zip(entity_types, num_entities_by_entity_type):
            entities[entity_field] = sorted(entities[entity_field].items(), key=lambda x: x[1], reverse=True)
            selected_entities[entity_field] = []

            for i in range(num_entities):
                try:
                    selected_entities[entity_field].append(entities[entity_field][i][0].title())
                    
                except:
                    break

        return selected_entities
