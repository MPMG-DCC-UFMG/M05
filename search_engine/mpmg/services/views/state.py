from unidecode import unidecode

from mpmg.services.models import State

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators, get_data_from_request

STATE = State()

class StateView(APIView):
    '''
    get:
        description: Retorna uma lista com todos estados ou um específico, se id_estado for especificado.
        parameters:
            - name: id_estado
              in: query
              description: ID do estado a ser buscado. 
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna uma lista de estados, ou um específico se id_estado for especificado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id: 
                                    type: string
                                    description: ID do bookmark.
                                codigo:
                                    type: string
                                    description: Código do estado, conforme IBGE.
                                sigla:
                                    type: string
                                    description: Sigla do estado.
                                nome:
                                    type: string
                                    description: Nome do estado.
            '404': 
                description: O estado não foi encontrado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem informando que o estado não foi encontrado.
    '''
    schema = AutoDocstringSchema()

    def get(self, request):
        if 'id_estado' in request.GET:
            state = STATE.get(request.GET['id_estado'])

            if state is None:
                return Response({'message': 'O estado não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(state, status=status.HTTP_200_OK)

        _, states = STATE.get_list(page='all')

        states.sort(key = lambda item: unidecode(item['nome']))

        return Response(states, status=status.HTTP_200_OK)