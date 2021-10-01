from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mpmg.services.models import *
from ..docstring_schema import AutoDocstringSchema


class DocumentView(APIView):
    '''
    get:
      description: Busca o conteúdo completo de um documento específico.
      parameters:
        - name: doc_id
          in: query
          description: ID do documento
          required: true
          schema:
            type: string
        - name: doc_type
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
        doc_type = request.GET['doc_type']
        doc_id = request.GET['doc_id']
        
        # instancia a classe apropriada e busca o registro no índice
        index_model_class_name = settings.SEARCHABLE_INDICES['regular'][doc_type]
        index_class = eval(index_model_class_name)
        
        document = index_class.get(doc_id)

        data = {
            'document': document
        }

        return Response(data)