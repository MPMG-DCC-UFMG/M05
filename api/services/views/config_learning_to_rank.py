from mpmg.services.models import ConfigLearningToRank
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mpmg.services.views.config_recommendation_evidence import CONF_REC_EVIDENCE

from ..docstring_schema import AutoDocstringSchema

from mpmg.services.utils import str2bool, get_data_from_request, validators

CONF_LTR = ConfigLearningToRank()

class ConfigLearningToRankView(APIView):
    '''
    get:
        description: Retorna uma lista de configuração de LTR ou um específico, se o ID dela for passado.        
        parameters:
            - name: id_conf_ltr
              in: query
              description: ID da configuração de LTR.
              required: false
              schema:
                    type: string
        responses:
            '200':
                description: Retorna uma lista de configuração de LTR ou um específico, se o ID dela for passado.    
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: ID da configuração de LTR.
                                    modelo:
                                        type: string
                                        description: Nome do modelo de LTR.
                                    quantidade:
                                        type: integer
                                        description: Quantidade de documentos do índice que será buscado.
                                    ativo:
                                        type: boolean
                                        description: Se deve ou não usar LTR.
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
        description: Cria uma nova configuração de LTR e retorna seu ID.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            modelo:
                                type: string
                                description: Nome do modelo de LTR.
                            quantidade:
                                type: integer
                                description: Quantidade de documentos a ser considerado.
                            ativo:
                                type: boolean
                                description: Se o LTR deve ou não ser ativado.
                        required:
                            - modelo
                            - quantidade
                            - ativo
        responses:
            '201':
                description: A configuração de LTR foi criada com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_conf_ltr: 
                                    type: string
                                    description: ID da configuração de LTR.
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
        description: Atualiza determinada configuração de LTR.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_conf_ltr:
                                type: string
                                description: ID da configuração de LTR.
                            modelo:
                                type: string
                                description: Nome do modelo de LTR.
                            quantidade:
                                type: integer
                                description: Quantidade de documentos a ser considerado.
                            ativo:
                                type: boolean
                                description: Se o LTR deve ou não ser ativado.                          
                        required:
                            - id_conf_ltr
        responses:
            '204':
                description: As alterações foram executadas com sucesso.
            '404':
                description: A configuração de LTR a ser alterada não existe ou não foi encontrada.
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
        description: Apaga uma configuração de LTR.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_conf_ltr:
                                type: string
                                description: ID da configuração de LTR.
                        required:
                            - id_conf_ltr
        responses:
            '204':
                description: Deleção com sucesso.
            '400':
                description: Não foi informado id_conf_ltr.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Menciona a necessidade de informar id_conf_ltr.
            '404':
                description: A configuração de fonte de LTR a ser deletada não existe ou não foi encontrada.
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

    def get(self, request):
        ltr_id = request.GET.get('id_conf_ltr')

        if ltr_id:
            source = CONF_LTR.get(ltr_id)

            if source is None:
                return Response({'message': 'A configuração de LTR não existe ou não foi encontradoa'}, status=status.HTTP_404_NOT_FOUND)

            return Response(source, status=status.HTTP_200_OK)

        _, ltr_confs = CONF_LTR.get_list(page='all')

        return Response(ltr_confs, status=status.HTTP_200_OK)


    def post(self, request):
        data = get_data_from_request(request)

        expected_fields = {'modelo', 'quantidade', 'ativo'}    

        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields)
        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)
        
        CONF_LTR.parse_data_type(data)

        id_conf_ltr = CONF_LTR.save(dict(
            modelo=data['modelo'],
            quantidade=data['quantidade'],
            ativo=data['ativo'],
        ))

        if id_conf_ltr:
            return Response({'id_conf_ltr': id_conf_ltr}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Não foi possível criar a configuração de LTR, tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

    def put(self, request):
        data = get_data_from_request(request)
        
        id_conf_ltr = data.get('id_conf_ltr')
        if id_conf_ltr is None:
            return Response({'message': 'Informe o ID da configuração de LTR a ser editada.'}, status.HTTP_400_BAD_REQUEST)
        del data['id_conf_ltr']
        
        conf_ltr = CONF_LTR.get(id_conf_ltr)

        if conf_ltr is None:
            return Response({'message': 'A configuração de LTR não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # campos que o usuário pode editar
        valid_fields = {'modelo', 'ativo', 'quantidade'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        CONF_LTR.parse_data_type(data)

        if CONF_LTR.item_already_updated(conf_ltr, data):
            return Response({'message': 'A configuração de LTR já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)

        success = CONF_LTR.update(id_conf_ltr, data)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a configuração de LTR, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = get_data_from_request(request)

        try:
            id_conf_ltr = data['id_conf_ltr']
        
        except KeyError:
            return Response({'message': 'Informe o ID da configuração de LTR a ser deletada.'}, status.HTTP_400_BAD_REQUEST)

        notification = CONF_LTR.get(id_conf_ltr)
        if notification is None:
           return Response({'message': 'A configuração de LTR não existe ou não foi encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        success = CONF_LTR.delete(id_conf_ltr)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível remover a configuração de LTR, tente novamente.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)