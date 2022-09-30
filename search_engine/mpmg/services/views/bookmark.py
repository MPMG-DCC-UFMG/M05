from mpmg.services.models import Bookmark
from mpmg.services.views.bookmark_folder import BOOKMARK, BOOKMARK_FOLDER
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators, get_data_from_request 

class BookmarkView(APIView):
    '''
    get:
        description: Busca o conteúdo de um favorito por meio de seu ID único. Também é possível buscar um favorito informando o índice e o ID do documento salvo pelo favorito, junto com o ID do usuaŕio
            que criou o favorito. Se somente o id do usuário for informado, retorna a lista de todos favoritos dele.
        parameters:
            - name: api_client_name
              in: path
              description: Nome do cliente da API. Passe "procon" ou "gsi".
              required: true
              schema:
                type: string
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

    def get(self, request, api_client_name):
        if 'id_favorito' in request.GET:
            bookmark = BOOKMARK.get(request.GET['id_favorito'])

        elif 'indice_documento' in request.GET and 'id_documento' in request.GET and 'id_usuario' in request.GET:
            indice_documento = request.GET['indice_documento']
            id_documento = request.GET['id_documento']
            id_usuario = request.GET['id_usuario']

            id_favorito = BOOKMARK.generate_id(id_usuario, indice_documento, id_documento)

            bookmark = BOOKMARK.get(id_favorito)

        elif 'id_usuario' in request.GET:
            id_usuario = request.GET['id_usuario']

            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(api_client_name, id_usuario)

            query = {'term': {'id_usuario.keyword': id_usuario}}
            client_filter = [{"term": { "nome_cliente_api": api_client_name}}]
            _, bookmarks = BOOKMARK.get_list(query,filter=client_filter, page='all')

            return Response(bookmarks, status=status.HTTP_200_OK)

        else:
            message = 'Informe o campo id_boomark ou indice_documento, id_documento e id_usuario ' + \
                        'ou apenas id_usuario, se deseja todos seus favoritos!'

            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        if bookmark is None:
            return Response({'message': 'O favorito não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(bookmark, status=status.HTTP_200_OK)
 

    def post(self, request, api_client_name):
        data = get_data_from_request(request)

        expected_fields = {'id_usuario', 'indice_documento', 'id_documento', 'id_consulta', 'nome'}
        optional_fields = {'id_sessao', 'id_pasta'}
        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields, optional_fields)

        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.POST['id_usuario']
        folder_id = request.POST.get('id_pasta') 

        if not folder_id:
            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(api_client_name, user_id)
            folder_id = BOOKMARK_FOLDER.get_default_bookmark_folder_id(api_client_name, user_id)

        parent_folder = BOOKMARK_FOLDER.get(api_client_name,folder_id)
        
        if parent_folder is None:
            return Response({'message': 'A pasta onde o bookmark seria salvo não existe.'}, status=status.HTTP_400_BAD_REQUEST)

        # O ID do bookmark é um hash do id do usuário com o indice e id do documento salvo
        generated_bookmark_id = BOOKMARK.generate_id(user_id, 
                                                    request.POST['indice_documento'], 
                                                    request.POST['id_documento'])
        
        bookmark = BOOKMARK.get(generated_bookmark_id)

        if bookmark:
            return Response({'message': 'O favorito já existe!'}, status=status.HTTP_400_BAD_REQUEST)

        BOOKMARK.parse_data_type(data)
        
        BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(api_client_name, user_id)

        session_id = request.POST.get('id_sessao', request.session.session_key)

        bookmark_id = BOOKMARK.save(dict(
            id_pasta=folder_id,
            id_usuario=user_id,
            indice_documento=request.POST['indice_documento'],
            id_documento=request.POST['id_documento'],
            id_consulta=request.POST['id_consulta'],
            id_sessao=session_id,
            nome=request.POST['nome'],
        ), generated_bookmark_id) 

        if bookmark_id is None:
            message = 'Não foi possível criar o favorito. Tente novamente!'
            return Response({'message': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'id_favorito': generated_bookmark_id}, status=status.HTTP_201_CREATED)        

    def put(self, request, api_client_name):
        data = get_data_from_request(request)

        bookmark_id = data.get('id_favorito')
        if bookmark_id is None:
            return Response({'message': 'É necessário informar o campo id_favorito.'}, status=status.HTTP_400_BAD_REQUEST)

        bookmark = Bookmark.get(bookmark_id)

        if bookmark is None:
            return Response({'message': 'O favorito não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        del data['id_favorito']
        
        valid_fields = {'id_pasta', 'nome'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        BOOKMARK.parse_data_type(data)
        if BOOKMARK.item_already_updated(bookmark, data):
            return Response({'message': 'O favorito já está atualizado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'id_pasta' in data:
            new_parent_folder_id = data['id_pasta']
            new_parent_folder = BOOKMARK_FOLDER.get(api_client_name, new_parent_folder_id)
            if new_parent_folder is None:
                return Response({'message': 'A pasta onde o bookmark seria movido não existe.'}, status=status.HTTP_400_BAD_REQUEST)

        if BOOKMARK.update(bookmark_id, data):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar o favorito, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, api_client_name):
        data = get_data_from_request(request)

        if 'id_favorito' not in data:
            return Response({'message': 'Informe o id_favorito com o ID do bookmark a ser deletado!'}, status.HTTP_400_BAD_REQUEST) 

        bookmark_id = data['id_favorito']
        
        bookmark = BOOKMARK.get(bookmark_id)
        if bookmark is None:
            return Response({'message': 'Bookmark não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if BOOKMARK.delete(bookmark_id):
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Não foi possível remover o favorito, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

