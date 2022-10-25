from unidecode import unidecode

from services.models import ProconCategory

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

PROCON_CATEGORY = ProconCategory()

class ProconCategoryView(APIView):
    '''
    get:
        description: Retorna a lista de categorias do procon.
        responses:
            '200':
                description: Retorna uma lista de categorias do procon.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id: 
                                    type: string
                                    description: ID da cidade.
                                cateogira:
                                    type: string
                                    description: Nome da categoria.
    '''

    schema = AutoDocstringSchema()

    def get(self, request):
        _, categories = PROCON_CATEGORY.get_list(page='all')
        categories.sort(key = lambda item: unidecode(item['categoria']))

        return Response(categories, status=status.HTTP_200_OK)
