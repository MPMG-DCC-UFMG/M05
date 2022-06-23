from rest_framework.views import APIView
from rest_framework.response import Response
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import APIConfig


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
            -   name: consulta
                in: query
                description: Consulta a ser levada em conta ao retornar as opções para o filtro de entidades. Requerido quando filtro="all" ou filtro="entities"
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

    def get(self, request, api_client_name, filtro):
        data = {}

        if (filtro == 'instances' or filtro == 'all') and api_client_name == 'gsi':
            data['instances'] = self._get_instances()
        if filtro == 'doc_types' or filtro == 'all':
            data['doc_types'] = self._get_doc_types(api_client_name)

        return Response(data)

    def _get_doc_types(self, api_client_name):
        active_indices = APIConfig.get_indices(api_client_name, group='regular', active=True)
        doc_types = []
        for item in active_indices:
            doc_types.append((item['ui_name'], item['es_index_name']))
        return doc_types

    def _get_instances(self):
        return ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2', 'Obras TCE']
