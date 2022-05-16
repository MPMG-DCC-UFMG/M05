from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import APIConfig


class SearchFilterView(APIView):
    '''
    get:
        description: Classe responsável por retornar a lista de itens das diferentes opções de filtros de busca
        parameters:
            -   name: filter_name
                in: path
                description: Nome do filtro que vc deseja buscar as opções. Passe "all" caso queira trazer as opções \
                    de todos os filtros. Lembrando que ao usar "all", vc deve passar o parâmetro query também.
                required: true
                schema:
                    type: string
                    enum:
                        - all
                        - instances
                        - doc_types
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

    def get(self, request, filter_name):
        data = {}

        if filter_name == 'instances' or filter_name == 'all':
            data['instances'] = self._get_instances()
        if filter_name == 'doc_types' or filter_name == 'all':
            data['doc_types'] = self._get_doc_types()

        return Response(data)

    def _get_doc_types(self):
        return [('Diários Oficiais','diarios'), ('Diários Segmentados', 'diarios_segmentado'), ('Processos','processos'), ('Licitações','licitacoes')]

    def _get_instances(self):
        return ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2','Obras TCE']