from unidecode import unidecode

from mpmg.services.models import ReclameAquiBusinessCategory

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

RECLAME_AQUI_BUSINESS_CATEGORY = ReclameAquiBusinessCategory()

class ReclameAquiBusinessCategoryView(APIView):
    '''
    get:
        description: Retorna a lista de categorias de empresa do Reclame Aqui.
        responses:
            '200':
                description: Retorna uma lista de categorias.
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
        _, categories = RECLAME_AQUI_BUSINESS_CATEGORY.get_list(page='all')
        categories.sort(key = lambda item: unidecode(item['categoria']))

        return Response(categories, status=status.HTTP_200_OK)
