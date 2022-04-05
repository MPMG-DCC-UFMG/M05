from collections import defaultdict

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from ..elastic import Elastic
from ..query_filter import QueryFilter

class SearchFilterView(APIView):
    '''
    get:
        description: Classe responsável por retornar a lista de itens das diferentes opções de filtros de busca
        parameters:
            -   name: filtro
                in: path
                description: Nome do filtro que vc deseja buscar as opções. Passe "all" caso queira trazer as opções \
                    de todos os filtros. Lembrando que ao usar "all", vc deve passar o parâmetro consulta também e se \
                        usar o filtro entities também.
                required: true
                schema:
                    type: string
                    enum:
                        - all
                        - instances
                        - doc_types
                        - entities
            -   name: consulta
                in: query
                description: Consulta a ser levada em conta ao retornar as opções para o filtro de entidades. Requerido quando filtro="all" ou filter_Name="entities"
                schema:
                    type: string
            -   name: filtro_instancias
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: string
            -   name: filtro_data_inicio
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: string
            -   name: filtro_data_fim
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: string
            -   name: filtro_tipo_documento
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
            -   name: filtro_entidade_pessoa
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_entidade_municipio
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_entidade_organizacao
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string
            -   name: filtro_entidade_local
                in: query
                description: Filtro a ser levado em conta ao retornar as opções do filtro de entidades.
                schema:
                    type: array
                    items:
                        type: string

    '''

    schema = AutoDocstringSchema()

    def get(self, request, filtro):
        data = {}

        if filtro == 'instances' or filtro == 'all':
            data['instances'] = self._get_instances()

        if filtro == 'doc_types' or filtro == 'all':
            data['doc_types'] = self._get_doc_types()

        if filtro == 'entities' or filtro == 'all':
            data['entities'] = self._get_dynamic_entities_filter(request)

        return Response(data)

    def _get_dynamic_entities_filter(self, request):
        consulta = request.GET['consulta']
        query_filter = QueryFilter.create_from_request(request)

        tipos_entidades = ['entidade_pessoa', 'entidade_municipio',
                           'entidade_local', 'entidade_organizacao']
        elastic = Elastic()

        indices = list(settings.SEARCHABLE_INDICES['regular'].keys())
        if len(query_filter.doc_types) > 0:
            indices = query_filter.doc_types

        must_clause = [elastic.dsl.Q(
            'query_string', query=consulta, fields=settings.SEARCHABLE_FIELDS)]
        filter_clause = query_filter.get_filters_clause()

        elastic_request = elastic.dsl.Search(using=elastic.es, index=indices) \
            .source(tipos_entidades) \
            .query("bool", must=must_clause, should=[], filter=filter_clause)

        response = elastic_request.execute()

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
                    entities[campo_entidade][ent.lower()] += 1

        # pegas as 10 entidades que mais aparecem
        selected_entities = {}
        for campo_entidade in tipos_entidades:
            entities[campo_entidade] = sorted(
                entities[campo_entidade].items(), key=lambda x: x[1], reverse=True)
            selected_entities[campo_entidade] = []
            for i in range(10):
                try:
                    selected_entities[campo_entidade].append(
                        entities[campo_entidade][i][0].title())
                except:
                    break
        return selected_entities

    def _get_doc_types(self):
        return [('Diários Oficiais', 'diarios'), ('Diários Segmentados', 'diarios_segmentado'), ('Processos', 'processos'), ('Licitações', 'licitacoes')]

    def _get_instances(self):
        return ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2', 'Obras TCE']
