from copyreg import constructor
from datetime import date, datetime

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import Bookmark
from mpmg.services.views.bookmark_folder import BOOKMARK, BOOKMARK_FOLDER

from ..docstring_schema import AutoDocstringSchema

class BookmarkView(APIView):
    '''
    get:
        description: Busca o conteúdo de um bookmark por meio de seu ID único, pelo índice e ID do documento que ele salva ou, se nenhum desses campos forem informado,
            retorna a lista de todos bookmarks do usuário.
        parameters:
            - name: bookmark_id
              in: query
              description: ID do bookmark. 
              required: false
              schema:
                    type: string
            - name: user_id
              in: query
              description: ID do usuário que criou o bookmark.
              required: false
              schema:
                    type: string
            - name: doc_index
              in: query
              description: Índice do documento salvo pelo bookmark. Use isso junto com doc_id para checar se um documento já possui bookmark.
              required: false
              schema:
                    type: string
            - name: doc_id
              in: query
              description: ID do documento salvo pelo bookmark. Use isso junto com doc_index para checar se um documento já possui bookmark.
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
                            user_id:
                                description: ID do usuário que está criando a pasta. 
                                type: string
                            folder_id:
                                description: ID da pasta onde será salvo o bookmark. Se esse campo não for informado, o bookmark será salvo na pasta default. 
                                type: string
                            doc_index:
                                description: Índice do documento salvo pelo bookmark.
                                type: string
                            doc_id:
                                description: ID do documento salvo pelo bookmark.
                                type: string
                            query_id:
                                description: ID da consulta.
                                type: string
                            name:
                                description: Nome do bookmark.
                                type: string
                        required:
                            - doc_index
                            - doc_id
                            - query_id
                            - name
        responses:
            '201':
                description: O bookmark foi criado com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                bookmark_id: 
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
                            bookmark_id:
                                description: ID do bookmark a ser alterado.
                                type: string
                            folder_id:
                                description: Nova pasta do bookmark, para onde ele será movido. 
                                type: string
                            name:
                                description: Novo nome do bookmark.
                                type: string
                        required:
                            - bookmark_id
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
                            bookmark_id:
                                description: ID do bookmark a ser removido.
                                type: string
                        required:
                            - bookmark_id      
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
        if 'bookmark_id' in request.GET:
            bookmark = Bookmark().get(request.GET['bookmark_id'])

        elif 'doc_index' in request.GET and 'doc_id' in request.GET and 'user_id' in request.GET:
            doc_index = request.GET['doc_index']
            doc_id = request.GET['doc_id']
            user_id = request.GET['user_id']

            bookmark_id = BOOKMARK.get_id(user_id, doc_index, doc_id)

            bookmark = BOOKMARK.get(bookmark_id)

        elif 'user_id' in request.GET:
            user_id = request.GET['user_id']

            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(user_id)

            bookmarks = BOOKMARK.get_all(user_id)
            return Response(bookmarks, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Informe os campos apropriadamente!'}, status=status.HTTP_400_BAD_REQUEST)

        if bookmark is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        return Response(bookmark, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            user_id = request.POST['user_id']

        except:
            return Response({'message': 'Informe o ID do usuário!'}, status=status.HTTP_400_BAD_REQUEST) 

        # pasta default onde são salvo os bookmarks do usuário
        folder_id = user_id

        if request.POST.get('folder_id'):
            folder_id = request.POST['folder_id'] 

        try:
            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(request.user.id)

            now = datetime.now().timestamp()
            bookmark_id = BOOKMARK.save(dict(
                id_pasta=folder_id,
                id_usuario=user_id,
                indice_documento=request.POST['doc_index'],
                id_documento=request.POST['doc_id'],
                id_consulta=request.POST['query_id'],
                id_sessao=request.session.session_key,
                nome=request.POST['name'],
                data_criacao=now,
                data_modificacao=now
            )) 

        except KeyError:
            msg_error = 'Informe corretamente os campos de criação de bookmark!'
            return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST) 

        if bookmark_id is None:
            return Response({"message": 'Não foi possível criar o bookmark. Tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'id_bookmark': bookmark_id}, status=status.HTTP_201_CREATED)        

    def put(self, request):
        data = request.data.dict()
        bookmark_id = data.get('bookmark_id')
        if not bookmark_id:
            return Response({'message': 'É necessário informar o campo bookmark_id!'}, status=status.HTTP_400_BAD_REQUEST)

        del data['bookmark_id']

        success, msg_error = BOOKMARK.update(bookmark_id, data)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        print(msg_error)

        return Response({'message': msg_error}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if 'bookmark_id' not in request.data:
            return Response({'message': 'Informe o bookmark_id!'}, status.HTTP_400_BAD_REQUEST) 

        bookmark_id = request.data['bookmark_id']

        print(type(bookmark_id))

        success, msg_error = BOOKMARK.remove(bookmark_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': msg_error}, status.HTTP_500_INTERNAL_SERVER_ERROR)

