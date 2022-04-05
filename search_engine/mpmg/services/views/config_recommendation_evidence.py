from mpmg.services.models import ConfigRecommendationEvidence
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema


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
                        properties:
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
        id_evidencia = request.GET.get('id_evidencia')
        tipo_evidencia = request.GET.get('tipo_evidencia')

        conf_rec_ev = ConfigRecommendationEvidence()

        if id_evidencia or tipo_evidencia:
            evidence, msg_error = conf_rec_ev.get(id_evidencia, tipo_evidencia)
            if evidence is None:
                return Response({'message': msg_error}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(evidence, status=status.HTTP_200_OK)
        
        active = request.GET.get('active')
        if active is not None:
            if active == 'false':
                active = False
        
            elif active == 'true':
                active = True
        
            else:
                active = False
        
        evidences, _ = conf_rec_ev.get(active=active)

        return Response(evidences, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.POST if len(request.POST) > 0 else request.data
        
        try:
            ev_repr = dict(
                nome = data['nome'],
                tipo_evidencia = data['tipo_evidencia'],
                nome_indice = data['nome_indice'],
                quantidade = data['quantidade'],
                similaridade_min = data['similaridade_min'],
                top_n_recommendacoes = data['top_n_recommendacoes'],
                active = data['active'],
            )
        except:
            return Response({'message': 'Informe todos os campos corretamente!'}, status=status.HTTP_400_BAD_REQUEST)

        
        conf_rec_ev = ConfigRecommendationEvidence()
        id_evidencia, msg_error = conf_rec_ev.save(ev_repr)

        if id_evidencia:
            return Response({'id_evidencia': id_evidencia}, status=status.HTTP_201_CREATED)

        return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _parse_data(self, data: dict):
        parsed_data = dict()
        for key, val in data.items():
            if '[' in key:
                s_key = key[:-1].split('[')
                index_name, attrib  = s_key[0], s_key[1]

                if index_name not in parsed_data:
                    parsed_data[index_name] = dict()
                
                if type(val) is str:
                    if val == 'false':
                        val = False
                    
                    elif val == 'true':
                        val = True 
                    
                    else:
                        val = int(val)
                    
                parsed_data[index_name][attrib] = val
                
        return parsed_data

    def put(self, request):
        data = request.data
        if type(data) is not dict:
            data = self._parse_data(data.dict())
        
        conf_rec_ev = ConfigRecommendationEvidence()

        error = dict()
        all_successfull = True
        for tipo_evidencia in data:
            config = data[tipo_evidencia]
            success, msg_error = conf_rec_ev.update(config, tipo_evidencia=tipo_evidencia)

            if not success:
                all_successfull = False 

            error[tipo_evidencia] = {
                'success': success,
                'message': msg_error 
            }

        if all_successfull:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        if type(data) is not dict:
            data = data.dict()

        id_evidencia = data.get('id_evidencia')
        tipo_evidencia = data.get('tipo_evidencia')

        conf_rec_ev = ConfigRecommendationEvidence()
        if id_evidencia or tipo_evidencia:
            evidence, msg_error = conf_rec_ev.get(id_evidencia, tipo_evidencia)
            if evidence is None:
                return Response({'message': 'Item não encontrado para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

            success, msg_error = conf_rec_ev.delete(id_evidencia, tipo_evidencia)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'É necessário informar "id_evidencia" ou "tipo_evidencia"!'}, status=status.HTTP_400_BAD_REQUEST)
