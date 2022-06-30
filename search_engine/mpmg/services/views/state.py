from mpmg.services.models import State

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from mpmg.services.utils import validators, get_data_from_request

STATE = State()

class StateView(APIView):
    schema = AutoDocstringSchema()

    def get(self, request):
        if 'id' in request.GET:
            state = STATE.get(request.GET['id'])

            if state is None:
                return Response({'message': 'O estado não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(state, status=status.HTTP_200_OK)

        states = STATE.get_list(page='all')
        return Response(states, status=status.HTTP_200_OK)            

    def post(self, request):
        pass 

    def put(self, request):
        pass 

    def delete(self, request):
        pass 