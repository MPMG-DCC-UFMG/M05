from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mpmg.services.models import config_rec_entities
from mpmg.services.models.config_rec_entities import ConfigRecEntity
from ..docstring_schema import AutoDocstringSchema

CONF_REC_ENTITY = ConfigRecEntity()

class ConfigRecEntityView(APIView):
    schema = AutoDocstringSchema()

    def get(self, request):
        _, conf_rec_entities = CONF_REC_ENTITY.get_list(page='all')
        return Response(conf_rec_entities, status=status.HTTP_200_OK)
