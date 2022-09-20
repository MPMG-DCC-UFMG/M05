from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User

from unittest.mock import patch
import requests

from elasticsearch import Elasticsearch

# Create your tests here.


def get_any_id():
    elastic_response = Elasticsearch().search(index="diarios", _source=False,
                                              body={
                                                  "size": 1,
                                                  "query": {
                                                      "match_all": {}
                                                  }
                                              })
    return elastic_response["hits"]["hits"][0]["_id"]

def get_auth_token():

    service_response = requests.post(settings.SERVICES_URL+'login', {'username': username, 'password': password})

    print(service_response.json())

def mustafa():
    print('hello')
    return {'k': 'kkk'}

class IndexTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        # get_auth_token()

        self.client = Client()

        # username = 'test_user'
        # email = 'test@email.com'
        # password = 'my_safe_password'

        # User.objects.get_or_create(username=username, email=email, password=password)

        # res = self.client.post(reverse('aduna:login'), data={'password': password, 'username': username})
        # print(res)
        
    # def test_request(self):
    #     # Issue a GET request.
    #     response = self.client.get(reverse('aduna:index'))

    #     # Check that the response is 200 OK.
    #     self.assertEqual(response.status_code, 200)

    @patch("aduna.views.index", autospec=True, side_effect=mustafa)
    def test_generate_session_id(self, mock_index):
        print('--')
        print(mock_index)
        print('++')

        # mock_get.return_value = {'k', 'asda'}
        # Issue a GET request.
        # response = self.client.get(reverse('aduna:index'))
        # print(response)
        # # Check that we have a session id.
        # self.assertTrue(response.context['sid'])


# class SearchTests(TestCase):

#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()

#     def test_request(self):
#         # Issue a GET request.
#         response = self.client.get(reverse('aduna:search'), {
#                                    'query': 'maria', 'page': 1, 'sid': 'sid', 'qid': ''})

#         # Check that the response is 200 OK.
#         self.assertEqual(response.status_code, 200)

#     def test_query_no_results(self):
#         # Issue a GET request.
#         response = self.client.get(reverse('aduna:search'), {
#                                    'query': '', 'page': 1, 'sid': 'sid', 'qid': ''})

#         # Check that the response is 200 OK.
#         self.assertEqual(response.status_code, 200)

#         # Check that the rendered context contains 0 results.
#         self.assertEqual(len(response.context['documents']), 0)


# class DocumentTests(TestCase):
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()

#     def test_request(self):
#         # Issue a GET request.

#         document_id = get_any_id()
#         response = self.client.get(reverse('aduna:document', kwargs={
#                                    'doc_type': 'diario', 'doc_id': document_id}))

#         # Check that the response is 200 OK.
#         self.assertEqual(response.status_code, 200)


# class LoginTests(TestCase):
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()

#     def test_request(self):
#         # Issue a GET request.
#         response = self.client.get(reverse('aduna:login'))

#         # Check that the response is 200 OK.
#         self.assertEqual(response.status_code, 200)
