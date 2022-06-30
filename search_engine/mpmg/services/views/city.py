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

    post:
        description: Cria um novo registro de cidade. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
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
                        required:
                            - codigo_cidade
                            - nome_cidade
                            - nome_estado
                            - sigla_estado
                            - codigo_estado
        responses:
            '201':
                description: O registro da nova cidade foi criada com sucesso. Retorna o ID da cidade recém-criado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_cidade: 
                                    type: string
                                    description: ID da cidade criada.
            '400':
                description: Algum(ns) do(s) campo(s) de criação foi(ram) informado(s) incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '500':
                description: Houve algum erro interno do servidor ao criar a cidade.
                content: 
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    put:
        description: Permite atualizar os campos de uma cidade. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_cidade:
                                description: ID da cidade a ser alterada.
                                type: string
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
                        required:
                            - id_cidade
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.
            '400':
                description: Algum campo editável da cidade foi informado incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: A cidade a ser alterada não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    delete:
        description: Apaga uma cidade.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_cidade:
                                description: ID da cidade a ser removida.
                                type: string
                        required:
                            - id_cidade      
        responses:
            '204':
                description: A cidade foi removida com sucesso.
            '400':
                description: O campo id_cidade não foi informado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: A cidade a ser deletada não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '500':
                description: Houve algum(ns) erro(s) interno durante o processamento.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
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