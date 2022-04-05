import hashlib
import random
import string
import time
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from mpmg.services.models import (LogSearch, LogSearchClick,
                                  LogSugestoes)
from mpmg.services.query import Query
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..docstring_schema import AutoDocstringSchema
from ..elastic import Elastic


class LogSearchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.GET.get('user_id',  None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        page = request.GET.get('page', 'all')

        if user_id == None and start_date == None and end_date == None:
            data = {'message': 'Pelo menos um parâmetro deve ser fornecido.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        elif start_date and end_date and start_date >= end_date:
            data = {'message': 'Data inicial deve ser anterior à data final.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        log_list = LogSearch.get_list_filtered(
            id_usuario=user_id, start_date=start_date, end_date=end_date, page=page)

        response = {
            "data": log_list
        }

        return Response(response)

    def post(self, request):
        '''
        Grava o log de uma consulta. Atualmente o log da consulta já está sendo
        gravado junto do método search da API. Mas ele está exposto aqui para o
        caso dessa dinâmica mudar e ser necessário chamar o método explicitamente.
        '''
        response = LogSearch().save(dict(
            id_sessao=request.POST['id_sessao'],
            id_consulta=request.POST['id_consulta'],
            id_usuario=int(request.POST['id_usuario']),
            text_consulta=request.POST['text_consulta'],
            algoritmo=request.POST['algoritmo'],
            data_hora=int(request.POST['data_hora']),
            tempo_resposta=float(request.POST['tempo_resposta']),
            pagina=int(request.POST['pagina']),
            resultados_por_pagina=int(request.POST['resultados_por_pagina']),
            documentos=request.POST.getlist('documentos'),
            tempo_resposta_total=float(request.POST['tempo_resposta_total']),
            indices=request.POST.getlist('indices'),
            instancias=request.POST.getlist('instancias'),
            data_inicial=request.POST['data_inicial'],
            data_final=request.POST['data_final'],
        ))

        # FIXME: Retorna o status HTTP correto
        return Response({"success": len(response[1]) == 0})


class LogSearchClickView(APIView):
    '''
    post:
      description: Grava no log o documento do ranking clicado pelo usuário.
      requestBody:
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                id_usuario: 
                  description: ID do usuário que clicou no item
                  type: string
                item_id:
                  description: ID do documento clicado
                  type: string
                qid:
                  description: ID da consulta executada (É sempre retornado pelo método search)
                  type: string
                posicao:
                  description: Posição do documento clicado na lista de documentos retornados
                  type: integer
                item_type:
                  description: Tipo do documento clicado
                  type: string
                  enum:
                  - diarios
                  - processos
                  - licitacoes
                page:
                  description: Número da página onde estava o documento
                  type: integer
                  minimum: 1
              required:
                - item_id
                - qid
                - posicao
                - item_type
                - page

    '''

    # permission_classes = (IsAuthenticated,)
    schema = AutoDocstringSchema()

    '''
    def get(self, request):
        id_consultas = request.GET.getlist('id_consultas', None)  # list of id_consulta
        log_list = LogSearchClick.get_list_filtered(id_consultas=id_consultas)
        response = {
            "data": log_list
        }
        return Response(response)
    '''

    def post(self, request):
        response = LogSearchClick().save(dict(
            id_usuario=request.POST['id_usuario'],
            id_documento=request.POST['item_id'],
            id_consulta=request.POST['qid'],
            posicao=request.POST['posicao'],
            tipo_documento=request.POST['item_type'],
            pagina=request.POST['page'],
            timestamp=int(time.time() * 1000),
        ))

        return Response({"success": len(response[1]) == 0})


class LogQuerySuggestionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = request.GET['query']
        resposta = LogSugestoes.get_suggestions(query)
        return Response({'sugestoes': resposta[1]})


class LogQuerySuggestionClickView(APIView):
    '''
    post:
      description: Grava no log a sugestão de consulta clicada pelo usuário
      requestBody:
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                sugestao:
                  description: Texto da sugestão clicada
                  type: string
                posicao:
                  description: Posição da sugestão clicada na lista de sugestões
                  type: integer
                  minimum: 1
              required:
                - sugestao
                - posicao
    '''
    # permission_classes = (IsAuthenticated,)
    schema = AutoDocstringSchema()

    def post(self, request):
        # FIXME: Criar método padronizado para obter timestamp
        timestamp = int(time.time() * 1000)

        posicao = request.POST.get('posicao', None)
        sugestao = request.POST.get('sugestao', None)

        response = LogSugestoes().save(dict(
            sugestao=sugestao,
            posicao=posicao,
            timestamp=timestamp
        ))

        return Response({"success": len(response[1]) == 0})


class LogDataGeneratorView():
    '''
    Entre no shell do django: 
        python manage.py shell
    Execute:
        from mpmg.services.views.log import *
        LogDataGeneratorView().clear_logs() # caso queira deletar os logs existentes
        LogDataGeneratorView().generate('01/08/2020', '25/08/2020')
    '''

    def generate(self, start_date, end_date):
        MAX_QUERIES_PER_DAY = 50
        POSSIBLE_QUERIES = ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim', 'Montes Claros', 'Ribeirão das Neves', 'Uberaba', 'Governador Valadares', 'Ipatinga', 'Sete Lagoas', 'Divinópolis', 'Santa Luzia', 'Ibirité', 'Poços de Caldas', 'Patos de Minas', 'Pouso Alegre', 'Teófilo Otoni', 'Barbacena', 'Sabará', 'Varginha', 'Conselheiro Lafaiete', 'Vespasiano', 'Itabira', 'Araguari', 'Ubá', 'Passos', 'Coronel Fabriciano', 'Muriaé', 'Araxá', 'Ituiutaba', 'Lavras', 'Nova Serrana', 'Itajubá', 'Nova Lima', 'Pará de Minas', 'Itaúna', 'Paracatu', 'Caratinga', 'Patrocínio', 'Manhuaçu', 'São João del Rei', 'Timóteo', 'Unaí', 'Curvelo', 'Alfenas', 'João Monlevade', 'Três Corações', 'Viçosa', 'Cataguases',
                            'Ouro Preto', 'Janaúba', 'São Sebastião do Paraíso', 'Esmeraldas', 'Januária', 'Formiga', 'Lagoa Santa', 'Pedro Leopoldo', 'Mariana', 'Ponte Nova', 'Frutal', 'Três Pontas', 'Pirapora', 'São Francisco', 'Congonhas', 'Campo Belo', 'Leopoldina', 'Lagoa da Prata', 'Guaxupé', 'Itabirito', 'Bom Despacho', 'Bocaiúva', 'Monte Carmelo', 'Diamantina', 'João Pinheiro', 'Santos Dumont', 'São Lourenço', 'Caeté', 'Santa Rita do Sapucaí', 'Igarapé', 'Visconde do Rio Branco', 'Machado', 'Almenara', 'Oliveira', 'Salinas', 'Andradas', 'Nanuque', 'Boa Esperança', 'Brumadinho', 'Arcos', 'Ouro Branco', 'Várzea da Palma', 'Iturama', 'Jaíba', 'Porteirinha', 'Matozinhos', 'Capelinha', 'Araçuaí', 'Extrema', 'São Gotardo', ]

        start_date = datetime.strptime(start_date, '%d/%m/%Y')
        end_date = datetime.strptime(end_date, '%d/%m/%Y')

        user_ids = []
        for user in User.objects.all():
            user_ids.append(user.id)

        # num_days = (start_date - end_date).days
        current_date = start_date
        while current_date < end_date:
            current_timestamp = int(datetime(
                year=current_date.year, month=current_date.month, day=current_date.day).timestamp() * 1000)

            # queries of the day
            num_queries = random.randrange(MAX_QUERIES_PER_DAY)
            day_queries = random.sample(POSSIBLE_QUERIES, num_queries)

            # add some random weird queries (to make sure we dont get results)
            # the number is based on the number of normal queries
            num_weird_queries = int(num_queries * random.random())
            num_words = random.randrange(2) + 1  # up to 3 words
            for q in range(num_weird_queries):
                weird_query = []
                for w in range(num_words+1):
                    # from 4 to 10 words' length
                    word_length = random.randrange(6) + 4
                    letters = string.ascii_lowercase
                    weird_query.append(''.join(random.choice(letters)
                                       for i in range(word_length)))
                weird_query = ' '.join(weird_query)
                day_queries.append(weird_query)
            # shuffle normal and weird queries
            random.shuffle(day_queries)

            print(current_date, num_queries)

            # execute queries
            for q in day_queries:

                sid = random.getrandbits(128)
                id_usuario = random.sample(user_ids, 1)[0]

                query_timestamp = current_timestamp + \
                    random.randrange(60*60*23) * \
                    1000  # add some hours and minutes
                query_timestamp = query_timestamp

                qid = hashlib.sha1()
                qid.update(bytes(str(query_timestamp) +
                           str(id_usuario) + q + str(sid), encoding='utf-8'))
                qid = qid.hexdigest()

                try:
                    query_obj = Query(
                        q, 1, qid, sid, id_usuario, use_entities=False)
                    query_obj.data_hora = query_timestamp
                    total_docs, total_pages, documents, took = query_obj.execute()
                except:
                    print('ERRO:', current_date, q)
                    continue

                # result click
                num_clicks = 0
                if len(documents) > 0:
                    num_clicks = random.choices(
                        [0, 1, 2, 3, 4], [5, 5, 1, 1, 1])

                    for _ in range(num_clicks[0]):
                        clicked_doc = random.sample(documents, 1)
                        clicked_doc = clicked_doc[0]

                        LogSearchClick().save(dict(
                            id_documento=clicked_doc.id,
                            id_consulta=qid,
                            posicao=clicked_doc.posicao,
                            tipo_documento=clicked_doc.type,
                            pagina=1,
                            # up to one minute to click in the result
                            timestamp=(query_timestamp + \
                                       random.randrange(60)*1000)
                        ))

                print(qid, q, 'vazio:', len(documents)
                      == 0, 'clicks:', num_clicks)

            current_date = current_date + timedelta(days=1)
        print('Finished')

    def clear_logs(self):
        elastic = Elastic()
        s = elastic.dsl.Search(using=elastic.es, index=['log_buscas', 'log_clicks'])\
            .update_from_dict({"query": {"match_all": {}}})

        response = s.delete()
        print(response)
