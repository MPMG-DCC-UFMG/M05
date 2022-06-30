from mpmg.services.models import City

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators, get_data_from_request

CITY = City()

class CityView(APIView):
    schema = AutoDocstringSchema()

    def get(self, request):
        if 'id' in request.GET:
            city = CITY.get(request.GET['id'])

            if city is None:
                return Response({'message': 'O município não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(city, status=status.HTTP_200_OK)

        elif 'filtro_estado' in request.GET:
            query = {'term': {'sigla_estado.keyword': request.GET['filtro_estado']}}
            _, cities = CITY.get_list(query, page='all')

        else:
            _, cities = CITY.get_list(page='all')

        return Response(cities, status=status.HTTP_200_OK)

    def post(self, request):
        pass 

    def put(self, request):
        pass 

    def delete(self, request):
        pass 