from ast import parse
from datetime import datetime
from typing import Dict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import ConfigRecommendation, config_recommendation

from ..docstring_schema import AutoDocstringSchema

EVIDENCE_TYPES = {'click', 'bookmark', 'query'}

class ConfigRecommendationView(APIView):
    # schema = AutoDocstringSchema()

    def _valid_data(self, data: dict):
        fields = set(data.keys())
        fields_diff = fields - EVIDENCE_TYPES
        return len(fields_diff) == 0
    
    def _parse_config(self, data: dict, key: str):
        if key.endswith('amount'):
            return {'amount': data[key]}
        
        elif key.endswith('min_similarity'):
            pass 

    def get(self, request, config):
        ConfigRecommendation().update_evidences("click", None)

    def post(self, request, config):
        pass 

    def put(self, request, config):
        data = request.data

        if type(data) != dict:
            data = data.dict()

        if not self._valid_data(data):
            return Response({'message': 'Informe somente os campos válidos!'}, status=status.HTTP_400_BAD_REQUEST)

        config_recommendation = ConfigRecommendation()
        if config == 'evidences':
            for evidency_type, conf in data.values():
                config_recommendation.update_evidences(evidency_type.upper(), conf)
                

        elif config == '':
            pass 

        else:
            return Response({'message': f'O parâmetro "{config}" não é válido!'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, config):
        pass 