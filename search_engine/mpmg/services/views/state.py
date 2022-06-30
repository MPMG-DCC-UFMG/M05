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
        description: Busca o conteúdo de um favorito por meio de seu ID único. Também é possível buscar um favorito informando o índice e o ID do documento salvo pelo favorito, junto com o ID do usuaŕio
            que criou o favorito. Se somente o id do usuário for informado, retorna a lista de todos favoritos dele.
        parameters:
            - name: id_favorito
              in: query
              description: ID do bookmark. 
              required: false
              schema:
                    type: string
            - name: id_usuario
              in: query
              description: ID do usuário que criou o bookmark.
              required: false
              schema:
                    type: string
            - name: indice_documento
              in: query
              description: Índice do documento salvo pelo bookmark. Use isso junto com id_documento para checar se um documento já possui bookmark.
              required: false
              schema:
                    type: string
            - name: id_documento
              in: query
              description: ID do documento salvo pelo bookmark. Use isso junto com indice_documento para checar se um documento já possui bookmark.
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna a representação do bookmark.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id: 
                                    type: string
                                    description: ID do bookmark.
                                id_pasta:
                                    type: string
                                    description: ID da pasta onde está salvo o bookmark.
                                indice_documento:
                                    type: string
                                    description: Índice do documento salvo pelo bookmark.
                                id_documento:
                                    type: string
                                    description: ID do documento salvo pelo bookmark.
                                id_consulta:
                                    type: string
                                    description: ID da consulta que originou a criação do bookmark.
                                id_sessao:
                                    type: string
                                    description: ID da sessão de criação do bookmark.
                                nome:
                                    type: string
                                    description: Nome do bookmark.
                                data_criacao:
                                    type: number
                                    description: Timestamp de quando o bookmark foi criado.
                                data_modificacao:
                                    type: number
                                    description: Timestamp da última modificação do bookmark.
            '400':
                description: Não foi informado os campos necessários para encontrar o(s) bookmark(s).
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
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
        description: Persiste a descrição de um favorito. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_usuario:
                                description: ID do usuário que está criando o favorito. 
                                type: string
                            id_pasta:
                                description: ID da pasta onde será salvo o favorito. Se esse campo não for informado, o favorito será salvo na pasta padrão "Favoritos" do usuário. 
                                type: string
                            indice_documento:
                                description: Índice do documento salvo pelo favorito.
                                type: string
                            id_documento:
                                description: ID do documento salvo pelo favorito.
                                type: string
                            id_consulta:
                                description: ID da consulta.
                                type: string
                            id_sessao:
                                description: ID da sessao. Se não for informado, será preenchido automaticamente com o ID da sessão atual.
                                type: string
                            nome:
                                description: Nome do favorito.
                                type: string
                        required:
                            - id_usuario
                            - indice_documento
                            - id_documento
                            - id_consulta
                            - nome
        responses:
            '201':
                description: O favorito foi criado com sucesso. Retorna o ID do favorito recém-criado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_favorito: 
                                    type: string
                                    description: ID do favorito criado.
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
                            id_favorito:
                                description: ID do favorito a ser alterado.
                                type: string
                            id_pasta:
                                description: Nova pasta do favorito, para onde ele será movido. 
                                type: string
                            nome:
                                description: Novo nome do favorito.
                                type: string
                        required:
                            - id_favorito
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.
            '400':
                description: Algum campo editável do favorito foi informado incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: O favorito a ser alterado não existe ou não foi encontrado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '400':
                description: Algum(ns) do(s) campo(s) a ser alterado foi(ram) informado(s) incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    delete:
        description: Apaga um favorito.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_favorito:
                                description: ID do favorito a ser removido.
                                type: string
                        required:
                            - id_favorito      
        responses:
            '204':
                description: O favorito foi removido com sucesso.
            '400':
                description: O campo id_favorito não foi informado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: O favorito a ser deletado não existe ou não foi encontrado.
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