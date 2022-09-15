from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..docstring_schema import AutoDocstringSchema
from mpmg.services.models import APIConfig, api_config

from ..elastic import Elastic
from ..models import Document

from elasticsearch_dsl.query import MoreLikeThis
from elasticsearch_dsl import Search


class SearchSimilar(APIView):
    '''
    get:
        description: Responsável por retornar uma lista de documentos similares a outro passado como parâmetro. Passe o tipo/nome do índice 
                    do documento e seu ID para retornar outros documentos similares a ele.
        parameters:
            -   name: api_client_name
                in: path
                description: Nome do cliente da API. Passe "procon" ou "gsi".
                required: true
                schema:
                    type: string
                    enum:
                        - procon
                        - gsi
            -   name: tipo_documento
                in: query
                description: Tipo/índice do documento.
                required: true
                schema:
                    type: string    
            -   name: id_documento
                in: query
                description: ID do documento.
                required: true
                schema:
                    type: string    
            -   name: max_num_documentos
                in: query
                description: Número máximo de documentos similares a serem retornados.
                required: false
                schema:
                    type: integer
                    default: 10
    '''                    
    schema = AutoDocstringSchema()
    api_config = APIConfig()

    def _get_valid_indices(self, api_client_name):
        results = self.api_config.get_indices(api_client_name)
        return set(result['es_index_name'] for result in results)

    def get(self, request, api_client_name):
        tipo_documento = request.GET.get('tipo_documento')
        id_documento = request.GET.get('id_documento')

        if tipo_documento is None:
            return Response({'message': 'É necessário informar o campo tipo_documento!'}, status=status.HTTP_400_BAD_REQUEST)

        if id_documento is None:
            return Response({'message': 'É necessário informar o campo tipo_documento!'}, status=status.HTTP_400_BAD_REQUEST)

        if tipo_documento not in self._get_valid_indices(api_client_name):
            return Response({'message': f'O índice "{tipo_documento}" é inválido!'}, status=status.HTTP_400_BAD_REQUEST)

        indices = [tipo_documento]

        docs = Document(api_client_name).search_similar(indices, tipo_documento, id_documento)

        return Response(docs, status=status.HTTP_200_OK)
