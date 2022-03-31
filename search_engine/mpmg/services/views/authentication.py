from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from ..docstring_schema import AutoDocstringSchema

from mpmg.services.models import BookmarkFolder

class CustomAuthToken(ObtainAuthToken):
    '''
    post:
      description: Autentica um usuário para fazer chamadas na API retornando o token de acesso em caso de sucesso
      requestBody:
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: Retorna o token de acesso à API juntamente com dados do usuário
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  user_info:
                    type: object
                    properties:
                      user_id:
                        type: integer
                      first_name:
                        type: string
                      last_name:
                        type: string
                      email:
                        type: string
        '401':
          description: Usuário não autorizado
    '''

    schema = None #AutoDocstringSchema()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        valid_user = serializer.is_valid(raise_exception=False)

        if valid_user:
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            BookmarkFolder().create_default_bookmark_folder_if_necessary(user.pk)
            return Response({
                'token': token.key,
                'user_info': {
                    'user_id': user.pk,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                },
            })
        else:
            return Response({
                'token': None,
                'user_info': None,
            }, status=status.HTTP_401_UNAUTHORIZED)


class TokenLogout(APIView):
    '''
    post:
      description: Apaga o token de acesso do usuário, impossibilitando que novas chamadas sejam feitas na API com o token antigo. \
                   Não requer nenhum parâmetro, apenas o Token no cabeçalho da requisição.
      security:
        - tokenAuth: []
    '''
    permission_classes = (IsAuthenticated,)
    schema = None

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'success': 'true'})