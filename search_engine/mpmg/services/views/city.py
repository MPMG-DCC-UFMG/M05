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
        if 'id_cidade' in request.GET:
            city = CITY.get(request.GET['id_cidade'])

            if city is None:
                return Response({'message': 'A cidade não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(city, status=status.HTTP_200_OK)

        elif 'filter_codigo_estado' in request.GET:
            query = {'term': {'codigo_estado.keyword': request.GET['filter_codigo_estado']}}
            _, cities = CITY.get_list(query, page='all')

        elif 'filter_sigla_estado' in request.GET:
            query = {'term': {'sigla_estado.keyword': request.GET['filter_sigla_estado']}}
            _, cities = CITY.get_list(query, page='all')

        else:
            _, cities = CITY.get_list(page='all')

        return Response(cities, status=status.HTTP_200_OK)

    def post(self, request):
        data = get_data_from_request(request)
        
        expected_fields = {'codigo_cidade', 'nome_cidade', 'nome_estado', 'sigla_estado', 'codigo_estado'}    

        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields)
        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        CITY.parse_data_type(data)

        city_id = CITY.save(dict(
            codigo_cidade = data['codigo_cidade'],
            nome_cidade = data['nome_cidade'],
            nome_estado = data['nome_estado'],
            sigla_estado = data['sigla_estado'],
            codigo_estado = data['codigo_estado']
        ))        

        if city_id:
            return Response({'id_municipio': city_id}, status=status.HTTP_200_OK)

        return Response({'message': 'Não foi possível criar o município, tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    def put(self, request):
        data = get_data_from_request(request)
        
        city_id = data.get('id_cidade')
        if city_id is None:
            return Response({'message': 'Informe o ID da cidade a ser editada.'}, status.HTTP_400_BAD_REQUEST)
        del data['id_cidade']

        city = CITY.get(city_id)

        if city is None:
            return Response({'message': 'A cidade não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        valid_fields = {'codigo_cidade', 'nome_cidade', 'nome_estado', 'sigla_estado', 'codigo_estado'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        CITY.parse_data_type(data)

        if CITY.item_already_updated(city, data):
            return Response({'message': 'A cidade já está atualizado.'}, status=status.HTTP_400_BAD_REQUEST)
        
                
        success = CITY.update(city_id, data)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a cidade, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = get_data_from_request(request)

        try:
            city_id = data['id_cidade']
        
        except KeyError:
            return Response({'message': 'Informe o ID da cidade a ser deletada.'}, status.HTTP_400_BAD_REQUEST)

        city = CITY.get(city_id)
        if city is None:
           return Response({'message': 'A cidade não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        success = CITY.delete(city_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível remover a cidade, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)         