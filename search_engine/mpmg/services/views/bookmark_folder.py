from mpmg.services.models import BookmarkFolder
from mpmg.services.models.bookmark import Bookmark
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators 

BOOKMARK_FOLDER = BookmarkFolder()
BOOKMARK = Bookmark()
class BookmarkFolderView(APIView):
    '''
    get:
        description: Retorna uma pasta específica, se id_pasta for informado, ou a árvore de pastas do usuário, se id_usuario for passado ao invés de id_pasta.
        parameters:
            - name: id_pasta
              in: query
              description: ID da pasta a ser buscada. 
              required: false
              schema:
                    type: string
            - name: id_usuario
              in: query
              description: ID do usuário a ter a árvore de pastas recuperadas.
              required: false
              schema:
                    type: string
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
                                id_usuario:
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
                                    description: Lista de subpastas.
                                    items:
                                        type: object
                                favoritos:
                                    type: array
                                    description: Lista de favoritos da pasta.
                                    items:
                                        type: string 
            '400':
                description: O campo id_pasta e id_usuario não foram informados.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: A pasta com ID informado não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    post:
        description: Cria uma pasta de bookmarks. 
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_usuario:
                                description: ID do usuário que está criando a pasta.
                                type: string
                            nome:
                                description: Nome da pasta a ser criada. 
                                type: string
                            id_pasta_pai:
                                description: ID da pasta que a pasta a ser criada será colocada. Se o campo não for
                                        informado, a pasta será criada na pasta default.
                                type: string
                        required:
                            - nome
                            - id_usuario
        responses:
            '201':
                description: O bookmark foi criado com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_pasta: 
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
            '500':
                description: Houve algum erro interno ao criar a pasta.
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
                            id_pasta:
                                description: ID da pasta a ser alterada.
                                type: string
                            nome:
                                description: Novo nome da pasta. 
                                type: string
                            id_pasta_pai:
                                description: ID da nova pasta pai. Isto é, da pasta que a pasta sendo alterada será movida.
                                type: string
                        required:
                            - id_pasta
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
            '500':
                description: Houve algum erro ao processar a requisição.
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
                            id_pasta:
                                description: ID da pasta a ser removido.
                                type: string
                        required:
                            - id_pasta      
        responses:
            '204':
                description: A pasta foi removida com sucesso.
            '400':
                description: O campo id_pasta foi informado incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '404':
                description: A pasta a ser deletada não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
            '500':
                description: Houve algum erro ao processar a requisição.
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
        folder_id = request.GET.get('id_pasta') 

        if folder_id:
            result = BOOKMARK_FOLDER.get(folder_id)
            if result is None:
                msg_error = f"Pasta não existe ou não foi encontrada."
                return Response({'message': msg_error}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result, status=status.HTTP_200_OK)
        
        else:
            user_id = request.GET.get('id_usuario')
            if not user_id:
                message = 'É necessário informar o id_pasta ou id_usuario.'
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST) 

            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(user_id)
            bookmark_folders = BOOKMARK_FOLDER.get_folder_tree(user_id)
            
            return Response(bookmark_folders, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            data = request.data.dict()
        
        except:
            data = request.data 

        expected_fields = {'id_usuario', 'nome'}    
        optional_fields = {'id_pasta_pai'}    
        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields, optional_fields)

        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = data['id_usuario']
        parent_folder_id = data.get('id_pasta_pai')

        if not parent_folder_id:
            BOOKMARK_FOLDER.create_default_bookmark_folder_if_necessary(user_id)
            parent_folder_id = user_id

        parent_folder = BOOKMARK_FOLDER.get(parent_folder_id)
        if parent_folder is None:
            return Response({'message': 'A pasta pai da pasta sendo criada não existe.'}, status=status.HTTP_400_BAD_REQUEST)

        folder_id = BOOKMARK_FOLDER.save(dict(
            criador = user_id,
            nome=data['nome'],
            id_pasta_pai=parent_folder_id
        ))
        
        if not bool(folder_id):
            return Response({'message': 'Não foi possível criar a pasta, tente novamente.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'id_pasta': folder_id}, status=status.HTTP_201_CREATED)        

    def put(self, request):
        try:
            data = request.data.dict()
        
        except:
            data = request.data 
        
        print('*' * 10)
        print(data)
        print('*' * 10)

        try:
            folder_id = data['id_pasta']
        
        except:
            message = 'O campo id_pasta com o ID da pasta a ser alterada deve ser informado!'
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        del data['id_pasta']

        folder = BOOKMARK_FOLDER.get(folder_id)

        if folder is None:
            return Response({'message': 'A pasta não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # campos que o usuário pode editar
        valid_fields = {'id_pasta_pai', 'nome'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        has_updated_fields = False 
        
        # se ao menos um campo a ser atualizado é diferente do atual 
        for field, value in data.items():
            if folder[field] != value:
                has_updated_fields = True 
                break 
        
        if not has_updated_fields:
            return Response({'message': 'A pasta já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'id_pasta_pai' in data:
            new_parent_folder_id = data['id_pasta_pai']
            new_parent_folder = BOOKMARK_FOLDER.get(new_parent_folder_id)
            if new_parent_folder is None:
                return Response({'message': 'A pasta para onde a pasta sendo alterada está sendo movida não existe.'}, status=status.HTTP_400_BAD_REQUEST)


        success = BOOKMARK_FOLDER.update(folder_id, data)

        if success:
            return Response(status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a pasta, tente novamente.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            data = request.data.dict()
        
        except:
            data = request.data 

        try:
            folder_id = data['id_pasta']
        
        except:
            message = 'O campo id_pasta com o ID da pasta a ser alterada deve ser informado!'
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        folder = BOOKMARK_FOLDER.get(folder_id)

        if folder is None:
            return Response({'message': 'A pasta não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if BOOKMARK_FOLDER.delete(folder_id):
            return Response(status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Não foi possível remover a pasta, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
