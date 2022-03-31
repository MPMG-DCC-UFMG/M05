from time import sleep
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import ConfigRecommendationSource

from ..docstring_schema import AutoDocstringSchema

class ConfigRecommendationSourceView(APIView):
    '''
    get:
        description: Retorna a lista de configuração de sources, podendo ser filtradas por ativas, ou uma configuração de source específica, se o ID ou índice do source for informado.
        parameters:
            - name: source_id
              in: query
              description: ID do source a ser recuperada.
              required: false
              schema:
                    type: string
            - name: index_name
              in: query
              description: Índice que a source remete.
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
                                        description: ID da source.
                                    ui_name:
                                        type: string
                                        description: Nome amigável que aparecerá ao usuário representando a source.
                                    es_index_name:
                                        type: string
                                        description: Índice que a source remente.
                                    amount:
                                        type: integer
                                        description: Quantidade de documentos do índice que será buscado.
                                    active:
                                        type: boolean
                                        description: Se a source deve ou não ser considerado para gerar recomendações.
    post:
        description: Cria uma nova source.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            ui_name:
                                type: string
                                description: Nome amigável que aparecerá ao usuário representando a source.
                            es_index_name:
                                type: string
                                description: Índice que a source remente.
                            amount:
                                type: integer
                                description: Quantidade de documentos do índice que será buscado.
                            active:
                                type: boolean
                                description: Se a source deve ou não ser considerado para gerar recomendações.
                        required:
                            - ui_name
                            - es_index_name
                            - amount
                            - active
        responses:
            '201':
                description: A source foi criada com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                source_id: 
                                    type: string
                                    description: ID da source criada.
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
        description: Atualiza determinada source. Para alterar uma source, passe um dicionário cuja chave seja o nome do índice que ela está atribuída e o valor é um dicionário com seus atributos alterados.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            index_name:
                                description: Dicionário onde a chave é o índice que a source está associada e o valor é um dicionário com os campos a serem alterados.
                                type: object                            
                        required:
                            - index_name
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
        description: Apaga uma source por seu ID ou índice associado, um dos dois precisa ser enviado.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
                            source_id:
                                type: string    
                                description: ID da source a ser removida.
                            index_name:
                                type: string
                                description: Índice associado ao source a ser removido.
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
        source_id = request.GET.get('source_id')
        index_name = request.GET.get('index_name')

        conf_rec_source = ConfigRecommendationSource()

        if source_id or index_name:
            source, msg_error = conf_rec_source.get(source_id, index_name)

            if source is None:
                return Response({'message': msg_error}, status=status.HTTP_404_NOT_FOUND)

            return Response(source, status=status.HTTP_200_OK)

        active = request.GET.get('active')
        if active is not None:
            if active == 'false':
                active = False
        
            elif active == 'true':
                active = True
        
            else:
                active = False

        
        sources, _ = conf_rec_source.get(active=active)
        return Response(sources, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.POST if len(request.POST) > 0 else request.data

        try:
            source_repr = dict(
                ui_name = data['ui_name'],
                es_index_name = data['es_index_name'],
                amount = data['amount'],
                active = data['active'],
            )
        except:
            return Response({'message': 'Informe todos os campos corretamente!'}, status=status.HTTP_400_BAD_REQUEST)

        conf_rec_source = ConfigRecommendationSource()
        source_id, msg_error = conf_rec_source.save(source_repr)

        if source_id:
            return Response({'source_id': source_id}, status=status.HTTP_201_CREATED)

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
        
        conf_rec_source = ConfigRecommendationSource()

        error = dict()
        all_successfull = True
        for index_name in data:
            config = data[index_name]
            success, msg_error = conf_rec_source.update(config, index_name=index_name)

            if not success:
                all_successfull = False

            error[index_name] = {
                'success': success,
                'message': msg_error 
            }

        if all_successfull:
            # para que o usuário atualize a página com os dados já atualizados
            sleep(.9)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(error, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        data = request.data
        if type(data) is not dict:
            data = data.dict()

        source_id = data.get('source_id')
        index_name = data.get('index_name')

        conf_rec_source = ConfigRecommendationSource()

        if source_id or index_name:
            source, msg_error = conf_rec_source.get(source_id, index_name)
            if source is None:
                return Response({'message': 'Item não encontrado para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

            success, msg_error = conf_rec_source.delete(source_id, index_name)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'É necessário informar "source_id" ou "index_name"!'}, status=status.HTTP_400_BAD_REQUEST)