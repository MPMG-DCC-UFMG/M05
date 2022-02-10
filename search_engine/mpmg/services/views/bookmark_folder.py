from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import BookmarkFolder
from mpmg.services.models.bookmark import Bookmark

from ..docstring_schema import AutoDocstringSchema

BOOKMARK_FOLDER = BookmarkFolder()
BOOKMARK = Bookmark()
class BookmarkFolderView(APIView):
    '''
    get:
        description: Retorna uma pasta específica, se folder_id for informado. Ou a árvore de pastas, se folder_id não for informado.
        parameters:
            - name: folder_id
                in: query
                description: ID da pasta a ser buscada. 
                required: false
                schema:
                        type: string
            - name: user_id
                in: query
                description: ID do usuário a ter a árvore de pastas recuperadas.
                required: 
        responses:
            '200':
                description: Retorna a representação de uma pasta ou a árvore de pastas, se folder_id não for informado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id: 
                                    type: string
                                    description: ID da pasta.
                                criador:
                                    type: string
                                    description: ID do criador da pasta. 
                                nome:
                                    type: string
                                    description: Nome da pasta. 
                                data_criacao:
                                    type: number
                                    description: Timestamp da criação da pasta. 
                                data_modificacao:
                                    type: number
                                    description: Timestamp da última data de modificação da pasta. 
                                pasta_pai:
                                    type: string
                                    description: ID da pasta pai, que esta pasta está contida. 
                                subpastas:
                                    type: array
                                    description: Lista de arquivos. Está lista será de IDs, se folder_id for 
                                        informado ou será objetos representando as subpastas da pasta.
                                    oneOf:
                                        - type: string
                                        - type: object
                                arquivos:
                                    type: array
                                    description: Lista de arquivos da pasta.
                                    items:
                                        type: string 
            '400':
                description: Não foi informado o ID do bookmark ou índice e ID do documento que ele salva.

    post:
        description: Cria uma pasta de bookmarks. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            user_id:
                                description: ID do usuário que está criando a pasta.
                                type: string
                            name:
                                description: Nome da pasta a ser criada. 
                                type: string
                            parent_folder_id:
                                description: ID da pasta que a pasta a ser criada será colocada. Se o campo não for
                                        informado, a pasta será criada na pasta default.
                                type: string
                        required:
                            - name
        responses:
            '201':
                description: O bookmark foi criado com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                folder_id: 
                                    type: string
                                    description: ID da pasta criada.
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
    put:
        description: Permite atualizar uma pasta já salva. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            folder_id:
                                description: ID da pasta a ser alterada.
                                type: string
                            name:
                                description: Novo nome da pasta. 
                                type: string
                            parent_folder_id:
                                description: ID da nova pasta pai. Isto é, da pasta que a pasta sendo alterada será movida.
                                type: string
                            subfolders:
                                type: array
                                description: Lista de IDs de subpastas da pasta.
                                items:
                                    type: string  
                            files:
                                type: array
                                description: Lista de IDs de bookmarks na pasta.
                                items:
                                    type: string 
                        required:
                            - folder_id
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
        description: Apaga uma pasta.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            folder_id:
                                description: ID da pasta a ser removido.
                                type: string
                        required:
                            - folder_id      
        responses:
            '204':
                description: A pasta foi removido com sucesso.
            '400':
                description: Informação de qual erro ocorreu.
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
        folder_id = request.GET.get('folder_id') 

        if folder_id:
            # retornar também os itens que estão na pasta do usuário
            result = BOOKMARK_FOLDER.get(folder_id)
            if result is None:
                msg_error = f"Não foi possível encontrar a pasta de ID {folder_id}. Certifique que este é um ID válido!"
                return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        
        else:
            user_id = request.GET.get('user_id')
            if not user_id:
                return Response({'message': 'É necessário informar o ID da pasta ou ID do usuário a ter a árvore de pastas retornada!'}, status=status.HTTP_400_BAD_REQUEST) 
            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(user_id)
            bookmark_folders = BOOKMARK_FOLDER.get_folder_tree(user_id)
            return Response(bookmark_folders, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            user_id = request.POST['user_id']

        except:
            return Response({'message': 'É necessário informar o ID do criador da pasta, por meio do campo user_id!'}, status=status.HTTP_400_BAD_REQUEST)

        parent_folder_id = request.POST.get('parent_folder_id')

        if not parent_folder_id:
            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(user_id)
            parent_folder_id = user_id

        data = dict(
            criador = user_id,
            nome=request.POST['name'],
            pasta_pai=parent_folder_id,
            subpastas=[],
            arquivos=[]
        )

        folder_id, msg_error = BOOKMARK_FOLDER.save(data)
        
        if not bool(folder_id):
            return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'folder_id': folder_id}, status=status.HTTP_201_CREATED)        

    def put(self, request):
        data = request.data.dict()

        try:
            folder_id = data['folder_id']
        
        except:
            msg_error = f'O campo "folder_id" deve ser informado!'
            return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST)


        del data['folder_id']
        success, msg_error = BOOKMARK_FOLDER.update(folder_id, data)

        if success:
            return Response(status.HTTP_204_NO_CONTENT)

        return Response({'message': msg_error}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        folder_id = request.data['folder_id']

        if BOOKMARK_FOLDER.remove_folder(folder_id, BOOKMARK):
            return Response(status.HTTP_204_NO_CONTENT)
        
        return Response({'message': f'Confira se "{folder_id}" é um ID válido e tente novamente!'}, status.HTTP_400_BAD_REQUEST)
