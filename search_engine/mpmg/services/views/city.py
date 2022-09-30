from unidecode import unidecode

from mpmg.services.models import City

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators, get_data_from_request

CITY = City()

class CityView(APIView):
    '''
    get:
        description: Retorna uma lista de cidades. Se filtro_sigla_estado ou filtro_codigo_estado for passado, a lista conterá 
            apenas as cidades do respectivo estado. Se um id específico for passado via id_cidade, somente essa cidade será retornada.
        parameters:
            - name: id_cidade
              in: query
              description: ID da ciade. 
              required: false
              schema:
                    type: string
            - name: filtro_sigla_estado
              in: query
              description: Sigla do estado para filtrar a lista de cidades.
              required: false
              schema:
                    type: string
            - name: filtro_codigo_estado
              in: query
              description: Codigo do estado para filtrar a lista de cidades.
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna uma lista de cidades ou uma cidade específica.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id: 
                                    type: string
                                    description: ID da cidade.
                                codigo_cidade:
                                    type: string
                                    description: Código da cidade, segundo IBGE.
                                nome_cidade:
                                    type: string
                                    description: Nome da cidade.
                                nome_estado:
                                    type: string
                                    description: Nome do estado.
                                sigla_estado:
                                    type: string
                                    description: Sigla do estado.
                                codigo_estado:
                                    type: string
                                    description: Código do estado, segundo IBGE.
            '404': 
                description: O bookmark não foi encontrado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem informando que o favorito não foi encontrado.
    '''
    schema = AutoDocstringSchema()

    def get(self, request):
        if 'id_cidade' in request.GET:
            city = CITY.get(request.GET['id_cidade'])

            if city is None:
                return Response({'message': 'A cidade não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(city, status=status.HTTP_200_OK)

        elif 'filtro_codigo_estado' in request.GET:
            query = {'term': {'codigo_estado.keyword': request.GET['filtro_codigo_estado']}}
            _, cities = CITY.get_list(query, page='all')

        elif 'filtro_sigla_estado' in request.GET:
            query = {'term': {'sigla_estado.keyword': request.GET['filtro_sigla_estado']}}
            _, cities = CITY.get_list(query, page='all')

        else:
            _, cities = CITY.get_list(page='all')

        cities.sort(key = lambda item: unidecode(item['nome_cidade']))

        return Response(cities, status=status.HTTP_200_OK)
