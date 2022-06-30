import pandas as pd
from mpmg.services.models import LogSearch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema


class QuerySuggestionView(APIView):
    '''
    get:
      description: Retorna uma lista de sugestões de consultas baseadas na consulta fornecida
      parameters:
        - name: consulta
          in: query
          description: Texto da consulta
          required: true
          schema:
            type: string
    '''

    schema = AutoDocstringSchema()

    def get(self, request, api_client_name):
        consulta = request.GET.get('consulta', None)
        
        if not consulta or len(consulta) < 1:
            data = {'message': 'Termo de consulta inválido.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        total, search_response = LogSearch.get_suggestions(api_client_name, consulta)
        processed_suggestions = []
        if total > 0:
            suggestions = pd.Series(
                search_response, name="texto_consulta").str.replace("\"", "").to_list()
            df = pd.DataFrame({"texto_consulta": suggestions})

            df = pd.Series(df.groupby(['texto_consulta'])[
                           'texto_consulta'].agg('count'))
            counts = df.to_list()
            suggestions = list(df.index)
            positions = [self._get_word_postion(
                element, consulta) for element in suggestions]
            df = pd.DataFrame({"suggestions": suggestions,
                              "count": counts, "position": positions})
            df = df.sort_values(['position', 'count'], ascending=[True, False])
            processed_suggestions = df.suggestions.to_list()

        data = {
            'suggestions': []
        }
        for i, hit in enumerate(processed_suggestions):
            data["suggestions"].append(
                {'label': hit, 'value': hit, 'posicao_ranking': i+1, 'suggestion_id': i+1})

        return Response(data)

    def _get_word_postion(self, element, consulta):
        for i, word in enumerate(element.split(" ")):
            if word.find(consulta) >= 0:
                return i
        return -1
