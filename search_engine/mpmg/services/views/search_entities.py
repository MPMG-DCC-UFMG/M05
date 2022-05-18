from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from ..elastic import Elastic
from ..query_filter import QueryFilter
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import APIConfig
import math

class SearchEntities(APIView):
    '''
    get:
        description: Classe responsável por retornar a lista de entidades relacionadas
        parameters:
            -   name: query
                in: query
                description: Consulta a ser levada em conta ao retornar as opções para o filtro de entidades. Requerido quando filter_name="all" ou filter_Name="entities"
                schema:
                    type: string
            -   name: filter_instances
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: string
            -   name: filter_start_date
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: string
            -   name: filter_end_date
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: string
            -   name: filter_doc_types
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
                        enum:
                            - diarios
                            - processos
                            - licitacoes
                            - diarios_segmentado
            -   name: filter_entidade_pessoa
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
            -   name: filter_entidade_municipio
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
            -   name: filter_entidade_organizacao
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
            -   name: filter_entidade_local
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string

    '''

    schema = AutoDocstringSchema()

    def get(self, request, strategy):
        data = self._get_entities(request, strategy)
        return Response(data)

    def _aggregate_strategies(self, total, score, strategy):
        if strategy == "votes":
            return 1
        if strategy == "combsum":
            return score
        if strategy == "expcombsum":
            return math.exp(score)
        if strategy == "max":
            return max(total, score)

    def _aggregate_scores(self, response, tipos_entidades, strategy):
        entities = {}
        for t in tipos_entidades:
            entities[t] = defaultdict(int)

        for doc in response:
            for campo_entidade in tipos_entidades:
                try:
                   entities_list = eval(doc[campo_entidade])
                except:
                    entities_list = []
                for ent in entities_list:
                    entities[campo_entidade][ent.lower()] += \
                        self._aggregate_strategies(
                            entities[campo_entidade][ent.lower()],
                            doc.meta.score,
                            strategy
                        )
        return entities

    def _get_entities(self, request, strategy):

        query = request.GET['query']

        query_filter = QueryFilter.create_from_request(request)


        # Pode ser pessoa, local, organizacao ou municio
        entity_type = request.GET.get('entity_type', 'all')

        if entity_type == 'all':
            tipos_entidades = ['entidade_pessoa', 'entidade_municipio', 'entidade_local', 'entidade_organizacao']

        else:
            tipos_entidades = [f'entidade_{entity_type}']

        elastic = Elastic()

        indices = APIConfig.searchable_indices('regular')
        if len(query_filter.doc_types) > 0:
            indices = query_filter.doc_types

        must_clause = [elastic.dsl.Q('query_string', query=query, fields=APIConfig.searchable_fields())]
        filter_clause = query_filter.get_filters_clause()

        elastic_request = elastic.dsl.Search(using=elastic.es, index=indices) \
                        .source(tipos_entidades) \
                        .query("bool", must = must_clause, should = [], filter = filter_clause)

        response = elastic_request.execute()

        entities =  self._aggregate_scores(response, tipos_entidades, strategy)
        
        num_entities = int(request.GET.get('num_entities', '10'))

        # pegas as num_entities entidades que mais aparecem
        selected_entities = {}
        for campo_entidade in tipos_entidades:
            entities[campo_entidade] = sorted(entities[campo_entidade].items(), key=lambda x: x[1], reverse=True)
            selected_entities[campo_entidade] = []
            for i in range(num_entities):
                try:
                    selected_entities[campo_entidade].append(entities[campo_entidade][i][0].title())
                except:
                    break

        return selected_entities if entity_type == 'all' else selected_entities[f'entidade_{entity_type}']
