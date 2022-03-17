from time import sleep

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import ConfigRecommendationEvidence

from ..docstring_schema import AutoDocstringSchema

class ConfigRecommendationEvidenceView(APIView):
    '''
    get:
        description: Retorna a lista de configuração de evidências, podendo ser filtradas por ativas, ou uma configuração de evidência específica, se o ID ou tipo da evidência for informado.
        parameters:
            - name: evidence_id
              in: query
              description: ID da evidência a ser recuperada.
              required: false
              schema:
                    type: string
            - name: evidence_type
              in: query
              description: Tipo da evidência a ser buscada.
              required: false
              schema:
                    type: string
            - name: active
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
                                    ui_name:
                                        type: string
                                        description: Nome amigável que aparecerá ao usuário representando o tipo da evidência.
                                    evidence_type:
                                        type: string
                                        description: Tipo da evidência.
                                    es_index_name:
                                        type: string
                                        description: Índice onde documentos representantes do tipo da evidência serão buscados.
                                    amount:
                                        type: integer
                                        description: Quantidade de documentos representantes do tipo de evidência que será buscado no índice correspondente.
                                    min_similarity:
                                        type: number
                                        description: Similaridade mínima entre um possível documento a ser recomendados e os documentos representantes do tipo de evidência para ser considerado válido.
                                    top_n_recommendations:
                                        type: integer
                                        description: Tamanho do ranking de documentos recomendados para o tipo de evidência.
                                    active:
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
                            ui_name:
                                type: string
                                description: Nome amigável do tipo de evidência.
                            evidence_type:
                                type: string
                                description: Tipo da evidência.
                            es_index_name:
                                type: string
                                description: Índice corresponde ao tipo de evidência.
                            amount:
                                type: integer
                                description: Quantidade de documentos representantes do tipo de evidência que será buscado no índice correspondente.
                            min_similarity:
                                type: number
                                description: Similaridade mínima entre um possível documento a ser recomendados e os documentos representantes do tipo de evidência para ser considerado válido.
                            top_n_recommendations:
                                type: integer
                                description: Tamanho do ranking de documentos recomendados para o tipo de evidência.
                            active:
                                type: boolean
                                description: Se o tipo de evidência deve ou não ser considerado para gerar recomendações.
                        required:
                            - ui_name
                            - evidence_type
                            - es_index_name
                            - amount
                            - min_similarity
                            - top_n_recommendations
                            - active
        responses:
            '201':
                description: O tipo de evidência foi criado com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                evidence_id: 
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
                            evidence_type:
                                description: Dicionário onde a chave é o tipo da evidência e o valor é um dicionário com os campos a serem alterados.
                                type: object                            
                        required:
                            - evidence_type
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
                            evidence_id:
                                type: string    
                                description: ID do tipo de evidência a ser removido.
                            evidence_type:
                                type: string
                                description: Tipo do tipo de evidência a ser removido.
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
                                    type: string
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
        evidence_id = request.GET.get('evidence_id')
        evidence_type = request.GET.get('evidence_type')

        conf_rec_ev = ConfigRecommendationEvidence()

        if evidence_id or evidence_type:
            evidence, msg_error = conf_rec_ev.get(evidence_id, evidence_type)
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
                ui_name = data['ui_name'],
                evidence_type = data['evidence_type'],
                es_index_name = data['es_index_name'],
                amount = data['amount'],
                min_similarity = data['min_similarity'],
                top_n_recommendations = data['top_n_recommendations'],
                active = data['active'],
            )
        except:
            return Response({'message': 'Informe todos os campos corretamente!'}, status=status.HTTP_400_BAD_REQUEST)

        
        conf_rec_ev = ConfigRecommendationEvidence()
        evidence_id, msg_error = conf_rec_ev.save(ev_repr)

        if evidence_id:
            return Response({'evidence_id': evidence_id}, status=status.HTTP_201_CREATED)

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
        for evidence_type in data:
            config = data[evidence_type]
            success, msg_error = conf_rec_ev.update(config, evidence_type=evidence_type)

            if not success:
                all_successfull = False 

            error[evidence_type] = {
                'success': success,
                'message': msg_error 
            }

        if all_successfull:
            # para dar tempo de o índice ter sido atualizado
            sleep(.9)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        if type(data) is not dict:
            data = data.dict()

        evidence_id = data.get('evidence_id')
        evidence_type = data.get('evidence_type')

        conf_rec_ev = ConfigRecommendationEvidence()
        if evidence_id or evidence_type:
            evidence, msg_error = conf_rec_ev.get(evidence_id, evidence_type)
            if evidence is None:
                return Response({'message': 'Item não encontrado para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

            success, msg_error = conf_rec_ev.delete(evidence_id, evidence_type)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'É necessário informar "evidence_id" ou "evidence_type"!'}, status=status.HTTP_400_BAD_REQUEST)