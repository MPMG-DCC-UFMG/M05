from mpmg.services.models import ConfigRecommendationSource
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema

class ConfigRecommendationSourceView(APIView):
    '''
    get:
        description: Retorna a lista de configuração de sources, podendo ser filtradas por ativas, ou uma configuração de source específica, se o ID ou índice do source for informado.
        parameters:
            - name: id_fonte
              in: query
              description: ID do source a ser recuperada.
              required: false
              schema:
                    type: string
            - name: nome_indice
              in: query
              description: Índice que a source remete.
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
    post:
        description: Cria uma nova source.
        requestBody:
            content:
                application/x-www-form-urlencoded:
                    schema:
                        type: object
                        properties:
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
                        required:
                            - nome
                            - nome_indice
                            - quantidade
                            - ativo
        responses:
            '201':
                description: A source foi criada com sucesso.
                content:
                    application/json:
                        schema:
                            type: object
                            properties: 
                                id_fonte: 
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
                            nome_indice:
                                description: Dicionário onde a chave é o índice que a source está associada e o valor é um dicionário com os campos a serem alterados.
                                type: object                            
                        required:
                            - nome_indice
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
                            id_fonte:
                                type: string    
                                description: ID da source a ser removida.
                            nome_indice:
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
        id_fonte = request.GET.get('id_fonte')
        nome_indice = request.GET.get('nome_indice')

        conf_rec_source = ConfigRecommendationSource()

        if id_fonte or nome_indice:
            source, msg_error = conf_rec_source.get(id_fonte, nome_indice)

            if source is None:
                return Response({'message': msg_error}, status=status.HTTP_404_NOT_FOUND)

            return Response(source, status=status.HTTP_200_OK)

        ativo = request.GET.get('ativo')
        if ativo is not None:
            if ativo == 'false':
                ativo = False

            elif ativo == 'true':
                ativo = True

            else:
                ativo = False

        sources, _ = conf_rec_source.get(ativo=ativo)
        return Response(sources, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.POST if len(request.POST) > 0 else request.data

        try:
            source_repr = dict(
                nome=data['nome'],
                nome_indice=data['nome_indice'],
                quantidade=data['quantidade'],
                ativo=data['ativo'],
            )
        except:
            return Response({'message': 'Informe todos os campos corretamente!'}, status=status.HTTP_400_BAD_REQUEST)

        conf_rec_source = ConfigRecommendationSource()
        id_fonte, msg_error = conf_rec_source.save(source_repr)

        if id_fonte:
            return Response({'id_fonte': id_fonte}, status=status.HTTP_201_CREATED)

        return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _parse_data(self, data: dict):
        parsed_data = dict()
        for key, val in data.items():
            if '[' in key:
                s_key = key[:-1].split('[')
                nome_indice, attrib = s_key[0], s_key[1]

                if nome_indice not in parsed_data:
                    parsed_data[nome_indice] = dict()

                if type(val) is str:
                    if val == 'false':
                        val = False

                    elif val == 'true':
                        val = True

                    else:
                        val = int(val)

                parsed_data[nome_indice][attrib] = val

        return parsed_data

    def put(self, request):
        data = request.data
        if type(data) is not dict:
            data = self._parse_data(data.dict())

        conf_rec_source = ConfigRecommendationSource()

        error = dict()
        all_successfull = True
        for nome_indice in data:
            config = data[nome_indice]
            success, msg_error = conf_rec_source.update(
                config, nome_indice=nome_indice)

            if not success:
                all_successfull = False

            error[nome_indice] = {
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

        id_fonte = data.get('id_fonte')
        nome_indice = data.get('nome_indice')

        conf_rec_source = ConfigRecommendationSource()

        if id_fonte or nome_indice:
            source, msg_error = conf_rec_source.get(id_fonte, nome_indice)
            if source is None:
                return Response({'message': 'Item não encontrado para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

            success, msg_error = conf_rec_source.delete(id_fonte, nome_indice)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'É necessário informar "id_fonte" ou "nome_indice"!'}, status=status.HTTP_400_BAD_REQUEST)
