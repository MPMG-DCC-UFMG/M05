from datetime import date, datetime

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import Bookmark

class BookmarkView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        
        if 'id_bookmark' in request.GET:
            bookmark = Bookmark().get_item(request.GET['id_bookmark'])

        else:
            index = request.GET['index']
            item_id = request.GET['item_id']

            bookmark = Bookmark().get_item_by_index_and_item_id(index, item_id)

        if bookmark is None:
            return Response({"success": False}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({"success": True, "bookmark": bookmark}, status=status.HTTP_200_OK)

    def post(self, request):
        id_folder = str(request.user.id)

        if request.POST.get('id_folder'):
            id_folder = request.POST['id_folder'] 

        id_bookmark = Bookmark().save(dict(
            id_folder=id_folder,
            nome=request.POST['nome'],
            index=request.POST['index'],
            item_id=request.POST['item_id'],
            consulta=request.POST['consulta'],
            id_sessao=request.session.session_key,
            data_criacao=str(datetime.now())
        )) 

        if id_bookmark is None:
            return Response({"success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": True, "id_bookmark": id_bookmark}, status=status.HTTP_201_CREATED)        

    def put(self, request):
        id_pasta_destino = request.data['id_pasta_destino']
        id_bookmark = request.data['id_bookmark']
        novo_nome = request.data['novo_nome']

        if Bookmark().update(id_bookmark, id_pasta_destino, novo_nome):
            return Response(status.HTTP_200_OK)

        return Response({"success": False, "msg": "Confira se os parâmetros estão corretos e tente novamente!"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id_bookmark = request.data['id_bookmark']

        if Bookmark().remove(id_bookmark):
            return Response(status.HTTP_200_OK)
        
        return Response({"success": False, "msg": f'Confira se "{id_bookmark}" é um ID válido e tente novamente!'}, status.HTTP_400_BAD_REQUEST)

