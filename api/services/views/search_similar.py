from curses.ascii import isalnum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..docstring_schema import AutoDocstringSchema
from services.models import APIConfig, api_config

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
                description: Número máximo de documentos similares a serem retornados. Deve ser um inteiro maior que 0.
                required: false
                schema:
                    type: integer
                    default: 10
        responses:
            '200':
                description: Retorna uma lista com os documentos encontrados
                content:
                    application/json:
                        schema:
                            type: array
                            description: Lista de documentos ordenados por relevância.
                            items:
                                type: object
            '400':
                description: Algum(ns) dos parâmetros foram passados incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem informado o parâmetro passado incorretamente.
    '''                    
    schema = AutoDocstringSchema()
    api_config = APIConfig()

    def _get_valid_indices(self, api_client_name):
        results = self.api_config.get_indices(api_client_name)
        return set(result['es_index_name'] for result in results)

    def get(self, request, api_client_name):
        doc_type = request.GET.get('tipo_documento')
        doc_id = request.GET.get('id_documento')
    
        if doc_type is None:
            return Response({'message': 'É necessário informar o campo tipo_documento!'}, status=status.HTTP_400_BAD_REQUEST)

        if doc_id is None:
            return Response({'message': 'É necessário informar o campo tipo_documento!'}, status=status.HTTP_400_BAD_REQUEST)

        if doc_type not in self._get_valid_indices(api_client_name):
            return Response({'message': f'O índice "{doc_type}" é inválido!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            max_num_docs = int(request.GET.get('max_num_documentos', '10'))
            if max_num_docs <= 0:
                raise ValueError('max_num_documentos deve ser maior que zero!')

        except:
            return Response({'message': '"max_num_documentos" deve ser um número inteiro maior que zero!'}, status=status.HTTP_400_BAD_REQUEST)

        indices = [doc_type]

        docs = Document(api_client_name).search_similar(indices, doc_type, doc_id, max_num_docs)

        return Response(docs, status=status.HTTP_200_OK)
