import time
import random

from django.http import response
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from .elastic import Elastic

def get_any_id(index="diarios"):
    elastic_response = Elastic().es.search(index = index, _source = False,\
            body = {
                "size": 1, 
                "query": {
                    "match_all": {}
                }
            })
    return elastic_response["hits"]["hits"][0]["_id"]

def get_auth_token(client):
    """
    Função que retorna o token utilizado como input para o header Authorization, necessário para
    autenticação via Django Rest Framework. Em nossos requests, o header é capitalizado e recebe
    o prefixo HTTP_ para ser passado nos requests GET e POST, segundo especificação do Django.
    Para mais informações, ver trecho que fala sobre headers e META keys em:
    https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.META
    """
    response = client.post(reverse('services:login'), {'username': 'testuser', 'password': '12345'})
    return response.json()['token']

class DocumentTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_document_request(self):
        # GET request enquanto logged in.
        document_id = get_any_id()
        response = self.client.get(reverse('services:document'), {'tipo_documento': 'diarios', 'id_documento': document_id, 'sid': '12345'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por documento retornado.
        self.assertIsNotNone(response['document'])

    def test_document_not_exists(self):
        document_id = "none"
        response = self.client.get(reverse('services:document'), {'tipo_documento': 'diarios', 'id_documento': document_id, 'sid': '12345'})
        self.assertEqual(response.status_code, 404)

class DocumentNavigationTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_document_request(self):
        document_id = get_any_id('diarios_segmentado')
        response = self.client.get(reverse('services:document_navigation'), {
                                   'tipo_documento': 'diarios_segmentado', 'id_documento': document_id})

        self.assertEqual(response.status_code, 200)

    def test_document_not_exists(self):
        document_id = random.randint(-10000, -1)
        response = self.client.get(reverse('services:document_navigation'), {
                                   'tipo_documento': 'diarios', 'id_documento': document_id})
        self.assertEqual(response.status_code, 404)

class LoginTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

    def test_invalid_login(self):
        # POST request para logar com senha errada.
        response = self.client.post(reverse('services:login'), {'username': 'testuser', 'password': '123'})

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

        # Response to JSON
        response = response.json()

        # Checa por auth_token == None
        self.assertIsNone(response['token'])

    def test_successful_login(self):
        # POST request para logar com senha correta.
        response = self.client.post(reverse('services:login'), {'username': 'testuser', 'password': '12345'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por auth_token != None
        self.assertIsNotNone(response['token'])

    def test_successful_logout(self):
        # POST request para deslogar
        auth_token = get_auth_token(self.client)
        response = self.client.post(reverse('services:logout'), HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por success == True
        self.assertTrue(response['success'])

class SearchTests(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_query_request(self):
        # GET request enquanto logged in.
        response = self.client.get(reverse('services:search'), {'consulta': 'maria', 'page': 1, 'sid': '123456789'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa pela resposta de autenticado.
        self.assertIsNotNone(response['consulta'])

    def test_invalid_query(self):
        # GET request enquanto logged in.
        response = self.client.get(reverse('services:search'), {'consulta': '', 'page': 1, 'sid': '123456789'})

        # Checa por response 400 Bad Request.
        self.assertEqual(response.status_code, 400)

        # Response to JSON
        response = response.json()

        # Checa que a mensagem de erro é 'invalid_query'.
        self.assertEqual(response['error_type'], 'invalid_query')

class ElasticTests(TestCase):
    def test_elastic_connection(self):
        #testar conexao com elastic
        ping_result = Elastic().es.ping()
        self.assertTrue(ping_result)

    def test_existence_elastic_indices(self):
        #testar se os indices existem
        indices_list = ["diarios", "processos", "log_buscas", "log_clicks"]
        indices_exist = Elastic().es.indices.exists(index=indices_list)
        self.assertTrue(indices_exist)

class LogSearchTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.current_time = int(time.time()*1000)
        self.log_search = {
                        'id_sessao': '123456789',
                        'id_consulta': 'test_query',
                        'id_usuario': 1,
                        'text_consulta': 'maria',
                        'algoritmo': 'BM25',
                        'data_criacao': self.current_time,
                        'tempo_resposta': 1.0,
                        'pagina': 1,
                        'resultados_por_pagina': 10,
                        'documentos': ['a','b','c'],
                        'tempo_resposta_total': 1.0,
                        'indices':'',
                        'instancias': '',
                        'data_inicial': '',
                        'data_final': '',
                        }
        self.log_click = {
                        'id_usuario': 1,
                        'id_documento': 'test_item_id',
                        'posicao': 1,
                        'tipo_documento': 'test_type',
                        'qid': 'test_query',
                        'pagina': 1
                        }

    def test_post_log_search_result_click(self):
        # POST request enquanto logged in.
        response = self.client.post(reverse('services:log_search_click'), self.log_click)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por success == True
        self.assertTrue(response['success'])

    def test_post_log_search_result_click_without_required_fields(self):
        fields = list(self.log_click.keys())

        # copia o registro de click sempre removendo um campo e checando se ao tentar
        # inserir isso no banco de dados não é aceito
        for field in fields:
            log_click = self.log_click.copy()
            del log_click[field]

            response = self.client.post(reverse('services:log_search_click'), log_click)
            self.assertEqual(response.status_code, 400)

class MetricTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.current_time = int(time.time()*1000)

class SuggestionTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_get_suggestion(self):
        # GET request enquanto logged in.
        response = self.client.get(reverse('services:query_suggestion'), {'consulta': 'maria'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_get_suggestion_empty_query(self):
        # GET request enquanto logged in.
        # Primeiro caso: sem passar 'query'
        response = self.client.get(reverse('services:query_suggestion'))

        # Checa por response 400 Bad Request.
        self.assertEqual(response.status_code, 400)

        # Segundo caso: passando query vazia
        response = self.client.get(reverse('services:query_suggestion'), {'consulta': ''})

        # Checa por response 400 Bad Request.
        self.assertEqual(response.status_code, 400)

class LogQuerySuggestionClickTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.log_query_suggestion_click = {
            'posicao': 0,
            'sugestao': 'some suggestion'
        }

    def test_post_log_query_suggestion_click(self):
        # POST request enquanto logged in.
        response = self.client.post(
            reverse('services:log_query_suggestion_click'), self.log_query_suggestion_click)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por success == True
        self.assertTrue(response['success'])

    def test_post_log_query_suggestion_click_without_required_fields(self):
        fields = list(self.log_query_suggestion_click.keys())

        # copia o registro de click sempre removendo um campo e checando se ao tentar
        # inserir isso no banco de dados não é aceito
        for field in fields:
            log_query_suggestion_click = self.log_query_suggestion_click.copy()
            del log_query_suggestion_click[field]

        response = self.client.post(
            reverse('services:log_query_suggestion_click'), log_query_suggestion_click)
        self.assertEqual(response.status_code, 200)

class MonitoringClusterTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_spected_cluster_info(self):
        spected_infos = {'cpu_percent', 'jvm_heap_size', 'jvm_heap_used'}
        response = self.client.get(reverse('services:monitoring_cluster'))

        self.assertEqual(response.status_code, 200)

        response_fields = set(response.json().keys())

        self.assertTrue(spected_infos == response_fields)


class SearchFilterTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _get_response_json(self, filtro, data = dict()):
        return self.client.get(reverse('services:search', 
            kwargs={'filtro': filtro}), data=data).json()

    def test_doctypes_search_filter(self):
        data = self._get_response_json('doc_types')

        doc_types = data.get('doc_types')
        instances = data.get('instances')

        # queremos que só um filtro tenha sido aplicado
        self.assertIsNotNone(doc_types)
        self.assertIsNone(instances)

    def test_instances_search_filter(self):
        data = self._get_response_json('instances')

        doc_types = data.get('doc_types')
        instances = data.get('instances')

        # queremos que só um filtro tenha sido aplicado
        self.assertIsNotNone(instances)
        self.assertIsNone(doc_types)

    def test_entities_search_filter(self):
        data = self._get_response_json('entities', {'consulta': 'maria'})

        doc_types = data.get('doc_types')
        instances = data.get('instances')

        # queremos que só um filtro tenha sido aplicado
        self.assertIsNone(doc_types)
        self.assertIsNone(instances)

    def test_all_search_filter(self):
        data = self._get_response_json('all', {'consulta': 'maria'})

        doc_types = data.get('doc_types')
        instances = data.get('instances')

        self.assertIsNotNone(doc_types)
        self.assertIsNotNone(instances)

