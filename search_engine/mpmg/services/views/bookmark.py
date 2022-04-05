from datetime import datetime

from mpmg.services.models import Bookmark
from mpmg.services.views.bookmark_folder import BOOKMARK, BOOKMARK_FOLDER
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema


class BookmarkView(APIView):
    '''
    get:
        description: Busca o conteúdo de um bookmark por meio de seu ID único, pelo índice e ID do documento que ele salva ou, se nenhum desses campos forem informado,
            retorna a lista de todos bookmarks do usuário.
        parameters:
            - name: id
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
                description: Não foi informado o ID do bookmark ou índice e ID do documento que ele salva.
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

    post:
        description: Persiste a descrição de um bookmark. 
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
                                description: ID da pasta onde será salvo o bookmark. Se esse campo não for informado, o bookmark será salvo na pasta default. 
                                type: string
                            indice_documento:
                                description: Índice do documento salvo pelo bookmark.
                                type: string
                            id_documento:
                                description: ID do documento salvo pelo bookmark.
                                type: string
                            id_consulta:
                                description: ID da consulta.
                                type: string
                            id_sessao:
                                description: TODO: (deixar ou não esse parâmetro?) ID da sessao.
                                type: string
                            nome:
                                description: Nome do bookmark.
                                type: string
                        required:
                            - id_usuario
                            - indice_documento
                            - id_documento
                            - id_consulta
                            - id_sessao
                            - nome
        responses:
            '201':
                description: O bookmark foi criado com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_bookmark: 
                                    type: string
                                    description: ID do bookmark.
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
                description: Houve algum erro interno do servidor ao criar o bookmark.
                content: 
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    put:
        description: Permite atualizar o nome e/ou pasta onde o bookmark foi salvo. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_bookmark:
                                description: ID do bookmark a ser alterado.
                                type: string
                            id_pasta:
                                description: Nova pasta do bookmark, para onde ele será movido. 
                                type: string
                            id_usuario:
                                description: ID do usuário. 
                                type: string
                            indice_documento:
                                description: Índice do documento salvo pelo bookmark.
                                type: string
                            id_documento:
                                description: ID do documento salvo pelo bookmark.
                                type: string
                            id_consulta:
                                description: ID da consulta.
                                type: string
                            id_sessao:
                                description: ID da sessao.
                                type: string
                            nome:
                                description: Novo nome do bookmark.
                                type: string
                        required:
                            - id_bookmark
        responses:
            '204':
                description: As alterações a serem feitas foram executadas com sucesso.
            
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
        description: Apaga um bookmark.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_bookmark:
                                description: ID do bookmark a ser removido.
                                type: string
                        required:
                            - id_bookmark      
        responses:
            '204':
                description: O bookmark foi removido com sucesso.
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

    # permission_classes = (IsAuthenticated,)
    schema = AutoDocstringSchema()

    def get(self, request):
        if 'id_bookmark' in request.GET:
            bookmark = Bookmark().get(request.GET['id_bookmark'])

        elif 'indice_documento' in request.GET and 'id_documento' in request.GET and 'id_usuario' in request.GET:
            indice_documento = request.GET['indice_documento']
            id_documento = request.GET['id_documento']
            id_usuario = request.GET['id_usuario']

            id_bookmark = BOOKMARK.get_id(id_usuario, indice_documento, id_documento)

            bookmark = BOOKMARK.get(id_bookmark)

        elif 'id_usuario' in request.GET:
            id_usuario = request.GET['id_usuario']

            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(id_usuario)

            bookmarks = BOOKMARK.get_all(id_usuario)
            return Response(bookmarks, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Informe os campos apropriadamente!'}, status=status.HTTP_400_BAD_REQUEST)

        if bookmark is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        return Response(bookmark, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            id_usuario = request.POST['id_usuario']

        except:
            return Response({'message': 'Informe o ID do usuário!'}, status=status.HTTP_400_BAD_REQUEST) 

        # pasta default onde são salvo os bookmarks do usuário
        folder_id = id_usuario

        if request.POST.get('folder_id'):
            folder_id = request.POST['folder_id'] 

        try:
            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(request.user.id)

            now = datetime.now().timestamp()
            id_bookmark = BOOKMARK.save(dict(
                id_pasta=folder_id,
                id_usuario=id_usuario,
                indice_documento=request.POST['indice_documento'],
                id_documento=request.POST['id_documento'],
                id_consulta=request.POST['id_consulta'],
                id_sessao=request.session.session_key,
                nome=request.POST['nome'],
                data_criacao=now,
                data_modificacao=now
            )) 

        except KeyError:
            msg_error = 'Informe corretamente os campos de criação de bookmark!'
            return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST) 

        if id_bookmark is None:
            return Response({"message": 'Não foi possível criar o bookmark. Tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'id_bookmark': id_bookmark}, status=status.HTTP_201_CREATED)        

    def put(self, request):
        # FIXME: Nem sempre o tipo request.data possui um método dict!

        data = request.data.dict()
        id_bookmark = data.get('id_bookmark')
        if not id_bookmark:
            return Response({'message': 'É necessário informar o campo id_bookmark!'}, status=status.HTTP_400_BAD_REQUEST)

        del data['id_bookmark']

        success, msg_error = BOOKMARK.update(id_bookmark, data)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': msg_error}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if 'id_bookmark' not in request.data:
            return Response({'message': 'Informe o id_bookmark!'}, status.HTTP_400_BAD_REQUEST) 

        id_bookmark = request.data['id_bookmark']

        success, msg_error = BOOKMARK.remove(id_bookmark)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)

