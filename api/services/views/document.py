from django.conf import settings
from elasticsearch.exceptions import NotFoundError
from services.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema


class DocumentView(APIView):
    '''
    get:
      description: Busca o conteúdo completo de um documento específico.
      parameters:
        - name: api_client_name
          in: path
          description: Nome do cliente da API. Passe "procon" ou "gsi".
          required: true
          schema:
            type: string
        - name: id_documento
          in: query
          description: ID do documento
          required: true
          schema:
            type: string
        - name: tipo_documento
          in: query
          description: Tipo do documento
          schema:
            type: string
            enum:
              - diarios
              - processos
              - licitacoes
    '''

    # permission_classes = (IsAuthenticated,)
    schema = AutoDocstringSchema()

    def get(self, request, api_client_name):
        tipo_documento = request.GET['tipo_documento']
        id_documento = request.GET['id_documento']

        # instancia a classe apropriada e busca o registro no índice
        index_class = APIConfig.searchable_index_to_class(api_client_name, 'regular')[tipo_documento]
        document = index_class.get(id_documento)
        if document:
            data = {
                'document': document
            }
            return Response(data)
        return Response(status=status.HTTP_404_NOT_FOUND)
