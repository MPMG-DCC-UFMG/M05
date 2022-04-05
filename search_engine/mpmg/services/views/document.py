from django.conf import settings
from elasticsearch.exceptions import NotFoundError
from mpmg.services.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema


class DocumentView(APIView):
    '''
    get:
      description: Busca o conteúdo completo de um documento específico.
      parameters:
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

    def get(self, request):
        tipo_documento = request.GET['tipo_documento']
        id_documento = request.GET['id_documento']

        # instancia a classe apropriada e busca o registro no índice
        index_model_class_name = settings.SEARCHABLE_INDICES['regular'][tipo_documento]
        index_class = eval(index_model_class_name)

        try:
            document = index_class.get(id_documento)

            data = {
                'document': document
            }

            return Response(data)
        
        except NotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
