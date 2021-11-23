from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import BookmarkFolder

class BookmarkFolderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        folder_id = request.GET.get('folder_id') 
        if folder_id:
            # retornar também os itens que estão na pasta do usuário
            result = BookmarkFolder().get_item(folder_id)
            if result is None:
                return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        
        else:
            BookmarkFolder().create_default_bookmark_folder_if_necessary(request.user.id)
            bookmark_folders = BookmarkFolder().get_folder_tree(request.user.id)
            return Response(bookmark_folders, status=status.HTTP_200_OK)

    def post(self, request):
        parent_folder = request.POST.get('pasta_pai')

        if not parent_folder:
            BookmarkFolder().create_default_bookmark_folder_if_necessary(request.user.id)
            parent_folder = str(request.user.id )

        folder_id = BookmarkFolder().save(dict(
            criador = str(request.user.id),
            nome=request.POST['nome'],
            pasta_pai=parent_folder,
            subpastas=[],
            arquivos=[]
        ))
        
        if folder_id is None:
            return Response({"success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": True, "folder_id": folder_id}, status=status.HTTP_201_CREATED)        

    def put(self, request):
        import random
        # atualiza uma pasta

        folder_id = request.data['folder_id']
        new_name = request.data['nome']

        if BookmarkFolder().rename(folder_id, new_name):
            return Response(status.HTTP_200_OK)

        return Response({"success": False, "msg": f"Confira se \"{folder_id}\" é um ID válido e tente novamente!"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        folder_id = request.data['folder_id']
        decision = request.data['decision']

        if BookmarkFolder().remove_folder(folder_id, decision):
            return Response(status.HTTP_200_OK)
        
        return Response({"success": False, "msg": f'Confira se "{folder_id}" é um ID válido e tente novamente!'}, status.HTTP_400_BAD_REQUEST)
