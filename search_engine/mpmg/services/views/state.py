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

    post:
        description: Salva o registro de um estado. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            codigo:
                                type: string
                                description: Código do estado, conforme IBGE.
                            sigla:
                                type: string
                                description: Sigla do estado.
                            nome:
                                type: string
                                description: Nome do estado.
                        required:
                            - codigo
                            - sigla
                            - nome
        responses:
            '201':
                description: O estado foi criado com sucesso. Retorna o ID do estado recém-criado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_estado: 
                                    type: string
                                    description: ID do estado criado.
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
                description: Houve algum erro interno do servidor ao criar o favorito.
                content: 
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    put:
        description: Permite atualizar o nome e/ou pasta onde o favorito foi salvo. É possível alterar o 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_estado:
                                description: ID do estado a ser alterado.
                                type: string
                            codigo:
                                type: string
                                description: Código do estado, conforme IBGE.
                            sigla:
                                type: string
                                description: Sigla do estado.
                            nome:
                                type: string
                                description: Nome do estado.
                        required:
                            - id_estado
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.
            '400':
                description: Algum campo editável do estado foi informado incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: O estado a ser alterado não existe ou não foi encontrado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
    delete:
        description: Apaga um estado.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_estado:
                                description: ID do estado a ser removido.
                                type: string
                        required:
                            - id_estado      
        responses:
            '204':
                description: O estado foi removido com sucesso.
            '400':
                description: O campo id_estado não foi informado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: O estado a ser deletado não existe ou não foi encontrado.
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
        if 'id_estado' in request.GET:
            state = STATE.get(request.GET['id_estado'])

            if state is None:
                return Response({'message': 'O estado não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(state, status=status.HTTP_200_OK)

        states = STATE.get_list(page='all')
        return Response(states, status=status.HTTP_200_OK)            

    def post(self, request):
        data = get_data_from_request(request)
        
        expected_fields = {'codigo', 'sigla', 'nome'}    

        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields)
        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        STATE.parse_data_type(data)

        state_id = STATE.save(dict(
            codigo = data['codigo'],
            sigla = data['sigla'],
            nome = data['nome']
        ))        

        if state_id:
            return Response({'id_estado': state_id}, status=status.HTTP_200_OK)

        return Response({'message': 'Não foi possível criar a estado, tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   

    def put(self, request):
        data = get_data_from_request(request)
        
        state_id = data.get('id_estado')
        if state_id is None:
            return Response({'message': 'Informe o ID do estado a ser editado.'}, status.HTTP_400_BAD_REQUEST)
        del data['id_estado']

        state = STATE.get(state_id)

        if state is None:
            return Response({'message': 'O estado não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        valid_fields = {'sigla', 'codigo', 'nome'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        STATE.parse_data_type(data)

        if STATE.item_already_updated(state, data):
            return Response({'message': 'O estado já está atualizado.'}, status=status.HTTP_400_BAD_REQUEST)
        
                
        success = STATE.update(state_id, data)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar o estado, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        data = get_data_from_request(request)

        try:
            state_id = data['id_estado']
        
        except KeyError:
            return Response({'message': 'Informe o ID do estado a ser deletado.'}, status.HTTP_400_BAD_REQUEST)

        state = STATE.get(state_id)
        if state is None:
           return Response({'message': 'O estado não existe ou não foi encontradao.'}, status=status.HTTP_404_NOT_FOUND)

        success = STATE.delete(state_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível remover o estado, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)