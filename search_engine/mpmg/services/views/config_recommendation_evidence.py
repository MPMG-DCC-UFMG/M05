from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

from mpmg.services.models import ConfigRecommendationEvidence
from mpmg.services.utils import str2bool, get_data_from_request, validators

CONF_REC_EVIDENCE = ConfigRecommendationEvidence()

class ConfigRecommendationEvidenceView(APIView):
    '''
    get:
        description: Retorna a lista de configuração de evidências, podendo ser filtradas por ativas, ou uma configuração de evidência específica, se o ID ou tipo da evidência for informado.
        parameters:
            - name: id_evidencia
              in: query
              description: ID da evidência a ser recuperada.
              required: false
              schema:
                    type: string
            - name: tipo_evidencia
              in: query
              description: Tipo da evidência a ser buscada.
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
                                        description: ID do tipo de evidência.
                                    nome:
                                        type: string
                                        description: Nome amigável que aparecerá ao usuário representando o tipo da evidência.
                                    tipo_evidencia:
                                        type: string
                                        description: Tipo da evidência.
                                    nome_indice:
                                        type: string
                                        description: Índice onde documentos representantes do tipo da evidência serão buscados.
                                    quantidade:
                                        type: integer
                                        description: Quantidade de documentos representantes do tipo de evidência que será buscado no índice correspondente.
                                    similaridade_min:
                                        type: number
                                        description: Similaridade mínima entre um possível documento a ser recomendados e os documentos representantes do tipo de evidência para ser considerado válido.
                                    top_n_recomendacoes:
                                        type: integer
                                        description: Tamanho do ranking de documentos recomendados para o tipo de evidência.
                                    ativo:
                                        type: boolean
                                        description: Se o tipo de evidência deve ou não ser considerado para gerar recomendações.
    post:
        description: Cria um novo tipo de evidência.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            nome:
                                type: string
                                description: Nome amigável do tipo de evidência.
                            tipo_evidencia:
                                type: string
                                description: Tipo da evidência.
                            nome_indice:
                                type: string
                                description: Índice corresponde ao tipo de evidência.
                            quantidade:
                                type: integer
                                description: Quantidade de documentos representantes do tipo de evidência que será buscado no índice correspondente.
                            similaridade_min:
                                type: number
                                description: Similaridade mínima entre um possível documento a ser recomendados e os documentos representantes do tipo de evidência para ser considerado válido.
                            top_n_recommendacoes:
                                type: integer
                                description: Tamanho do ranking de documentos recomendados para o tipo de evidência.
                            ativo:
                                type: boolean
                                description: Se o tipo de evidência deve ou não ser considerado para gerar recomendações.
                        required:
                            - nome
                            - tipo_evidencia
                            - nome_indice
                            - quantidade
                            - similaridade_min
                            - top_n_recommendacoes
                            - ativo
        responses:
            '201':
                description: O tipo de evidência foi criado com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_evidencia: 
                                    type: string
                                    description: ID do tipo de evidência criada.
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
        description: Atualiza determinado tipo de evidência. Para alterar uma evidência, passe um dicionário cuja chave seja o tipo de evidência e o valor é um dicionário com seus atributos alterados.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:get_list
                            tipo_evidencia:
                                description: (TODO: adicionar a possibilidade de fazer por ID) Dicionário onde a chave é o tipo da evidência e o valor é um dicionário com os campos a serem alterados.
                                type: object                            
                        required:
                            - tipo_evidencia
        responses:
            '204':
                description: As alterações foram executadas com sucesso.
            '400':
                description: Algum campo foi informado incorretamente.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: string
                                    description: Mensagem de erro.
    delete:
        description: Apaga um tipo de evidência por seu ID ou tipo, um dos dois precisa ser enviado.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            id_evidencia:
                                type: string    
                                description: ID do tipo de evidência a ser removievidence_idvido.
        responses:
            '204':
                description: Deleção com sucesso.
            '400':
                description: Nenhum dos campos foi enviado.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                message: 
                                    type: stringevidence_id
                                    description: Menciona a necessidade de informar pelo menos um dos campos válido.
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
        evidence_type = request.GET.get('tipo_evidencia')
        evidence_conf_id = request.GET.get('id_conf_evidencia', evidence_type)

        if evidence_conf_id:
            evidence = CONF_REC_EVIDENCE.get(evidence_conf_id)
            if evidence is None:
                return Response({'message': 'Configuração de evidência não existe ou não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(evidence, status=status.HTTP_200_OK)
        
        active = request.GET.get('ativo')
        if active is not None:
            active = str2bool(active)

        conf_rec_evidences = CONF_REC_EVIDENCE.get(active=active)

        return Response(conf_rec_evidences, status=status.HTTP_200_OK)

    def post(self, request):
        data = get_data_from_request(request)

        expected_fields = {'nome', 'tipo_evidencia', 'nome_indice', 'quantidade', 'similaridade_minima', 'top_n_recomendacoes', 'ativo'}
        optional_fields = {}
        all_fields_available, unexpected_fields_message = validators.all_expected_fields_are_available(data, expected_fields, optional_fields)

        if not all_fields_available:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        conf_evidence = CONF_REC_EVIDENCE.get(data['tipo_evidencia'])
        if conf_evidence is not None:
            return Response({'message': 'Só pode haver uma configuração de recomendação de evidência por índice.'}, status=status.HTTP_400_BAD_REQUEST)

        CONF_REC_EVIDENCE.parse_data_type(data)
        conf_evidence_id = CONF_REC_EVIDENCE.save(dict(
                nome = data['nome'],
                tipo_evidencia = data['tipo_evidencia'],
                nome_indice = data['nome_indice'],
                quantidade = data['quantidade'],
                similaridade_minima = data['similaridade_minima'],
                top_n_recomendacoes = data['top_n_recomendacoes'],
                ativo = data['ativo'],
            ), data['tipo_evidencia']
        )

        if conf_evidence_id is None:
            return Response({'message': 'Não foi possível criar a configuração de evidência. Tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'id_conf_evidencia': conf_evidence_id}, status=status.HTTP_201_CREATED)

    def put(self, request):
        data = get_data_from_request(request)

        evidence_type = data.get('tipo_evidencia')
        evidence_conf_id = data.get('id_conf_evidencia', evidence_type)

        if evidence_conf_id is None:
            return Response({'message': 'É necessário informar tipo_evidencia ou id_evidencia para alteração.'}, status=status.HTTP_400_BAD_REQUEST)

        conf_rec_evidence = CONF_REC_EVIDENCE.get(evidence_conf_id) 
        if conf_rec_evidence is None:
            return Response({'message': 'Configuração de evidência não existe ou não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if 'tipo_evidencia' in data:
            del data['tipo_evidencia']

        if 'id_conf_evidencia' in data:
            del data['id_conf_evidencia']
            
        valid_fields = {'similaridade_minima', 'quantidade', 'top_n_recomendacoes', 'ativo', 'nome'} 
        data_fields_valid, unexpected_fields_message = validators.some_expected_fields_are_available(data, valid_fields)

        if not data_fields_valid:
            return Response({'message': unexpected_fields_message}, status=status.HTTP_400_BAD_REQUEST)

        CONF_REC_EVIDENCE.parse_data_type(data)

        if CONF_REC_EVIDENCE.item_already_updated(conf_rec_evidence, data):
            return Response({'message': 'A configuração da evidência já está atualizada.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if CONF_REC_EVIDENCE.update(evidence_conf_id, data):
             return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Não foi possível atualizar a configuração da evidência. Tente novamente!'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = get_data_from_request(request)
        
        tipo_evidencia = data.get('tipo_evidencia')
        conf_evidence_id = data.get('id_conf_evidencia', tipo_evidencia)

        if conf_evidence_id is None:
            return Response({'message': 'É necessário informar id_conf_evidencia ou tipo_evidencia!'}, status=status.HTTP_400_BAD_REQUEST)

        evidence = CONF_REC_EVIDENCE.get(conf_evidence_id)
        if evidence is None:
            return Response({'message': 'A configuração de evidência não existe ou não foi encontrada!'}, status=status.HTTP_404_NOT_FOUND)

        if CONF_REC_EVIDENCE.delete(conf_evidence_id):
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Não foi possível deletar a configuração de evidência. Tente novamente!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

