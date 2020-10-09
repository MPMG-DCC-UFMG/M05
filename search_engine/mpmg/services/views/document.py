from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mpmg.services.models import *
from mpmg.services.models import SearchableIndicesConfigs

class DocumentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        doc_type = request.GET['doc_type']
        doc_id = request.GET['doc_id']
        
        # instancia a classe apropriada e busca o registro no índice
        index_model_class_name = SearchableIndicesConfigs.get_index_model_class_name(doc_type)
        index_class = eval(index_model_class_name)
        
        document = index_class.get(doc_id)

        data = {
            'document': document
        }

        return Response(data)