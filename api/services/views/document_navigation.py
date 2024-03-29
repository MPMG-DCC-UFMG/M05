from elasticsearch.exceptions import NotFoundError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from ..elastic import Elastic

class DocumentNavigationView(APIView):
    '''
    get:
        description: Retorna uma lista com todas as seções do documento a ser visualizado. \
        Caso a consulta e as entidades sejam passadas, as seções que contiverem os termos da consulta ou as entidades serão destacadas.
        parameters:
            -   name: api_client_name
                in: path
                description: Nome do cliente da API. Passe "procon" ou "gsi".
                required: true
                schema:
                    type: string
            -   name: id_documento
                in: query
                description: ID do documento (ou segmento) a ser buscado
                required: true
                schema:
                    type: string
            -   name: tipo_documento
                in: query
                description: Tipo do documento
                required: true
                schema:
                    type: string
                    enum:
                        - diarios
                        - processos
                        - licitacoes
                        - diarios_segmentado
            -   name: consulta
                in: query
                description: Texto da consulta, para ter a seção onde a consulta aparece destacada.
                schema:
                    type: string
            -   name: filtro_entidade_pessoa
                in: query
                description: Lista de entidades do tipo pessoa. Seções que contiverem estas entidades serão destacadas
                schema:
                    type: array
            -   name: filtro_entidade_municipio
                in: query
                description: Lista de entidades do tipo município. Seções que contiverem estas entidades serão destacadas
                schema:
                    type: array
            -   name: filtro_entidade_organizacao
                in: query
                description: Lista de entidades do tipo organização. Seções que contiverem estas entidades serão destacadas
                schema:
                    type: array
            -   name: filtro_local
                in: query
                description: TODO
                schema:
                    type: array       
    '''

    schema = AutoDocstringSchema()

    def get(self, request, api_client_name):
        try:
            id_documento = request.GET['id_documento']
            # o tipo do documento é o nome do índice
            index_name = request.GET['tipo_documento']
            query = request.GET.get('consulta', None)
            filtro_entidade_pessoa = request.GET.getlist(
                'filtro_entidade_pessoa', [])
            filtro_entidade_municipio = request.GET.getlist(
                'filtro_entidade_municipio', [])
            filtro_entidade_organizacao = request.GET.getlist(
                'filtro_entidade_organizacao', [])
            local_filter = request.GET.getlist('filtro_local', [])

            self.elastic = Elastic()

            # primeiro recupera o registro do segmento pra poder pegar o ID do pai
            retrieved_doc = self.elastic.dsl.Document.get(
                id_documento, using=self.elastic.es, index=index_name)
            id_pai = retrieved_doc['id_pai']

            search_obj = self.elastic.dsl.Search(
                using=self.elastic.es, index=index_name)
            search_obj.source(['entidade_bloco', 'titulo', 'num_bloco',
                            'num_segmento_bloco', 'num_segmento_global'])
            query_param = {"match": {"id_pai": id_pai}}
            sort_param = {'num_segmento_global': {'order': 'asc'}}

            # faz a consulta uma vez pra pegar o total de segmentos
            search_obj = search_obj.query(self.elastic.dsl.Q(query_param))
            elastic_result = search_obj.execute()
            total_records = elastic_result.hits.total.value

            # refaz a consulta trazendo todos os segmentos
            search_obj = search_obj[0:total_records]
            search_obj = search_obj.sort(sort_param)
            elastic_result = search_obj.execute()

            # faz mais uma vez pra buscar os segmentos que casam com a consulta
            matched_segments = []
            if query != None:
                search_obj = self.elastic.dsl.Search(
                    using=self.elastic.es, index=index_name)
                must_queries = [self.elastic.dsl.Q(
                    'query_string', query=query), self.elastic.dsl.Q(query_param)]
                # , filter = filter_queries)
                search_obj = search_obj.query("bool", must=must_queries)
                search_obj = search_obj[0:total_records]
                # search_obj = search_obj.sort(sort_param)
                query_result = search_obj.execute()

                for item in query_result:
                    matched_segments.append(int(item.num_segmento_global))

            navigation = []
            for item in elastic_result:
                entidade_bloco = item.entidade_bloco.title(
                ) if hasattr(item, 'entidade_bloco') else ''
                titulo = item.titulo.title() if hasattr(item, 'titulo') else ''
                num_bloco = int(item.num_bloco) if hasattr(
                    item, 'num_bloco') else -1
                num_segmento_bloco = int(item.num_segmento_bloco) if hasattr(
                    item, 'num_segmento_bloco') else -1
                num_segmento_global = int(item.num_segmento_global) if hasattr(
                    item, 'num_segmento_global') else -1
                matched = 1 if num_segmento_global in matched_segments else 0

                if num_segmento_bloco == 1:
                    navigation.append({'entidade_bloco': entidade_bloco, 'num_bloco': num_bloco, 'childs': [
                                    {'titulo': titulo, 'num_segmento_bloco': num_segmento_bloco, 'num_segmento_global': num_segmento_global, 'matched': matched}]})
                else:
                    navigation[-1]['childs'].append({'titulo': titulo, 'num_segmento_bloco': num_segmento_bloco,
                                                    'num_segmento_global': num_segmento_global, 'matched': matched})

            data = {
                'navigation': navigation
            }
            
            return Response(data)

        except NotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
