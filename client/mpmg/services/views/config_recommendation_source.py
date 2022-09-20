from mpmg.services.models import ConfigRecommendationSource
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mpmg.services.views.config_recommendation_evidence import CONF_REC_EVIDENCE

from ..docstring_schema import AutoDocstringSchema

from mpmg.services.utils import str2bool, get_data_from_request, validators

CONF_REC_SOURCE = ConfigRecommendationSource()

class ConfigRecommendationSourceView(APIView):
    '''
    get:
        description: Retorna a lista de configuração de fontes de recomendação, podendo ser filtradas por ativas, ou uma configuração de fonte específica, se o ID for informado.
        parameters:
            - name: api_client_name
              in: path
              description: Nome do cliente da API. Passe "procon" ou "gsi".
              required: true
              schema:
                type: string
            - name: id_conf_fonte
              in: query
              description: ID do source a ser recuperada.
              required: false
              schema:
                    type: string
            - name: ativo
              in: query
              description: Se a lista retorna só possui elementos ativos.
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna uma configuração de evidência ou uma lista dela.
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: ID da source.
                                    nome_cliente_api:
                                        type: string
                                        description: Nome do cliente da API.
                                    nome:
                                        type: string
                                        description: Nome amigável que aparecerá ao usuário representando a source.
                                    nome_indice:
                                        type: string
                                        description: Índice que a source remente.
                                    quantidade:
                                        type: integer
                                        description: Quantidade de documentos do índice que será buscado.
                                    ativo:
                                        type: boolean
                                        description: Se a source deve ou não ser considerado para gerar recomendações.
            '404': 
                description: A configuração de fonte de recomendação não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem informando que a configuração de fonte de recomendação não existe ou não foi encontrada.
    post:
        description: Cria uma nova configuração de fonte de recomendação.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            nome:
                                type: string
                                description: Nome amigável que aparecerá ao usuário representando a configuração de fonte de recomendação.
                            nome_indice:
                                type: string
                                description: Índice que a configuração de fonte de recomendação remete.
                            quantidade:
                                type: integer
                                description: Quantidade de documentos do índice que serão buscados.
                            ativo:
                                type: boolean
                                description: Se a fonte de recomendação deve ou não ser considerado para gerar recomendações.
                        required:
                            - nome
                            - nome_indice
                            - quantidade
                            - ativo
        responses:
            '201':
                description: A configuração de fonte de recomendação foi criada com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_fonte: 
                                    type: string
                                    description: ID da configuração de fonte de recomendação criada.
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
                description: Houve algum(ns) erro(s) interno durante o processamento.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.

    put:
        description: Atualiza determinada configuração de fonte de recomendação.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_conf_fonte:
                                type: string
                                description: ID da configuração de fonte de recomendação a ser alterada.
                            nome:
                                type: string
                                description: Nome amigável que aparecerá ao usuário representando a configuração de fonte de recomendação.
                            quantidade:
                                type: integer
                                description: Quantidade de documentos do índice que serão buscados.
                            ativo:
                                type: boolean
                                description: Se a fonte de recomendação deve ou não ser considerado para gerar recomendações.                            
                        required:
                            - id_conf_fonte
        responses:
            '204':
                description: As alterações foram executadas com sucesso.
            '404':
                description: A configuração de fonte de recomendação a ser alterada não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
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
        description: Apaga uma source por seu ID ou índice associado, um dos dois precisa ser enviado.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_conf_fonte:
                                type: string    
                                description: ID da source a ser removida.
                        required:
                            - id_conf_fonte
        responses:
            '204':
                description: Deleção com sucesso.
            '400':
                description: Não foi informado id_conf_fonte.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Menciona a necessidade de informar id_conf_fonte.
            '404':
                description: A configuração de fonte de recomendação a ser deletada não existe ou não foi encontrada.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
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
    schema = AutoDocstringSchema()

    def get(self, request, api_client_name):
        source_id = request.GET.get('id_conf_fonte')

        if source_id:
            source = CONF_REC_SOURCE.get(source_id)

            if source is None:
                return Response({'message': 'A configuração de recomendação de fonte não existe ou não foi encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(source, status=status.HTTP_200_OK)

        active = request.GET.get('ativo')
        if active is not None:
            active = str2bool(active)

        conf_rec_sources = CONF_REC_SOURCE.get(api_client_name, active=active)
        return Response(conf_rec_sources, status=status.HTTP_200_OK)

    def post(self, request, api_client_name):
        data = get_data_from_request(request)
  
        expected_fields = {'nome', 'nome_indice', 'quantidade', 'ativo'}
        optional_fields = {}
        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields, optional_fields)

        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        conf_source = CONF_REC_SOURCE.get(api_client_name,source_id=data['nome_indice'])
        if conf_source is not None:
            return Response({'message': 'Só pode haver uma configuração de recomendação de fonte por índice.'}, status=status.HTTP_400_BAD_REQUEST)

        CONF_REC_EVIDENCE.parse_data_type(data)

        source_id = CONF_REC_SOURCE.save(dict(
            nome=data['nome'],
            nome_cliente_api=api_client_name,
            nome_indice=data['nome_indice'],
            quantidade=data['quantidade'],
            ativo=data['ativo'],
        ), data['nome_indice'])

        if source_id is None:
            return Response({'message': 'Não foi possível criar a configuração de fonte de recomendação. Tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'id_conf_fonte': source_id}, status=status.HTTP_201_CREATED)

    def put(self, request, api_client_name):
        data = get_data_from_request(request)

        source_conf_id = data.get('id_conf_fonte') 

        if source_conf_id is None:
            return Response({'message': 'É necessário informar nome_indice ou id_conf_fonte para alteração.'}, status=status.HTTP_400_BAD_REQUEST)

        conf_rec_source = CONF_REC_SOURCE.get(api_client_name, source_id=source_conf_id)

        if conf_rec_source is None:
            return Response({'message': 'Configuração de fonte de recomendação não existe ou não encontrada'}, status=status.HTTP_404_NOT_FOUND)        

        if 'nome_indice' in data:
            del data['nome_indice']

        if 'id_conf_fonte' in data:
            del data['id_conf_fonte']

        valid_fields = {'quantidade', 'ativo', 'nome'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        CONF_REC_SOURCE.parse_data_type(data)
        if CONF_REC_SOURCE.item_already_updated(conf_rec_source, data):
            return Response({'message': 'A configuração de fonte de recomendação já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)

        if CONF_REC_SOURCE.update(source_conf_id, data):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a configuração de fonte de recomendação. Tente novamente.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, api_client_name):
        data = get_data_from_request(request)        
        conf_source_id = data.get('id_conf_fonte')

        if conf_source_id is None:
            return Response({'message': 'É necessário informar id_conf_fonte ou nome_indice!'}, status=status.HTTP_400_BAD_REQUEST)

        conf_source = CONF_REC_SOURCE.get(api_client_name,source_id=conf_source_id)
        if conf_source is None:
            return Response({'message': 'Configuração de fonte de recomendação não encontrada para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

        if CONF_REC_SOURCE.delete(conf_source_id):
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Não foi possível deletar a configuração de fonte de recomendação. Tente novamente.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

