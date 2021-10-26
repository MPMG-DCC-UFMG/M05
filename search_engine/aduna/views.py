import re
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, response
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from collections import defaultdict


def index(request):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    context = {
        'user_name': request.session.get('user_info')['first_name'],
        'services_url': settings.SERVICES_URL,
        'auth_token': request.session.get('auth_token'),
    }
    return render(request, 'aduna/index.html', context)


def search(request):
    if request.GET.get('invalid_query', False) or not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    sid = request.session.session_key
    query = request.GET['query']
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    filter_instances = request.GET.getlist('filter_instances', [])
    filter_doc_types = request.GET.getlist('filter_doc_types', [])
    filter_start_date = request.GET.get('filter_start_date', None)
    if filter_start_date == "":
        filter_start_date = None
    filter_end_date = request.GET.get('filter_end_date', None)
    if filter_end_date == "":
        filter_end_date = None
    filter_entidade_pessoa = request.GET.getlist('filter_entidade_pessoa', [])
    filter_entidade_municipio = request.GET.getlist('filter_entidade_municipio', [])
    filter_entidade_organizacao = request.GET.getlist('filter_entidade_organizacao', [])
    filter_entidade_local = request.GET.getlist('filter_entidade_local', [])

    # busca as opções do filtro
    params = {
        'query': query, 
        'filter_instances': filter_instances, 
        'filter_doc_types': filter_doc_types,
        'filter_start_date': filter_start_date,
        'filter_end_date': filter_end_date,
        'filter_entidade_pessoa': filter_entidade_pessoa,
        'filter_entidade_municipio': filter_entidade_municipio,
        'filter_entidade_organizacao': filter_entidade_organizacao,
        'filter_entidade_local': filter_entidade_local,
    }
    filter_response = requests.get(settings.SERVICES_URL+'search_filter/all', params, headers=headers)
    filter_content = filter_response.json()
    filter_instances_list = filter_content['instances']
    filter_doc_types_list = filter_content['doc_types']
    filter_entities_list = filter_content['entities']


    
    # faz a busca
    params = {
        'query': query, 
        'page': page, 
        'sid': sid, 
        'qid': qid, 
        'filter_instances': filter_instances, 
        'filter_doc_types': filter_doc_types,
        'filter_start_date': filter_start_date,
        'filter_end_date': filter_end_date,
        'filter_entidade_pessoa': filter_entidade_pessoa,
        'filter_entidade_municipio': filter_entidade_municipio,
        'filter_entidade_organizacao': filter_entidade_organizacao,
        'filter_entidade_local': filter_entidade_local,
    }
    service_response = requests.get(settings.SERVICES_URL+'search', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')

    else:
        context = {
            'auth_token': request.session.get('auth_token'),
            'user_name': request.session.get('user_info')['first_name'],
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': response_content['time'],
            'qid': response_content['qid'],
            'total_docs': response_content['total_docs'],
            'results_per_page': range(response_content['results_per_page']),
            'documents': response_content['documents'],
            'total_pages': response_content['total_pages'],
            'results_pagination_bar': range(min(9, response_content['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
            'filter_start_date': datetime.strptime(response_content['filter_start_date'], '%Y-%m-%d') if response_content['filter_start_date'] != None else None,
            'filter_end_date': datetime.strptime(response_content['filter_end_date'], '%Y-%m-%d') if response_content['filter_end_date'] != None else None,
            'filter_instances': response_content['filter_instances'],
            'filter_doc_types': response_content['filter_doc_types'],
            'filter_instances_list': filter_instances_list,
            'filter_doc_types_list': filter_doc_types_list,
            'filter_entities_list': filter_entities_list,
            'filter_entidade_pessoa': filter_entidade_pessoa,
            'filter_entidade_municipio': filter_entidade_municipio,
            'filter_entidade_organizacao': filter_entidade_organizacao,
            'filter_entidade_local': filter_entidade_local,
            'filter_url': '&pessoa='+'&pessoa='.join(filter_entidade_pessoa)+'&municipio='+'&municipio='.join(filter_entidade_municipio)+'&organizacao='+'&organizacao='.join(filter_entidade_organizacao)+'&local='+'&local='.join(filter_entidade_local)
        }
        
        return render(request, 'aduna/search.html', context)
    

def document(request, doc_type, doc_id):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}
    sid = request.session.session_key
    service_response = requests.get(settings.SERVICES_URL+'document', {'doc_type': doc_type, 'doc_id': doc_id}, headers=headers)

    if service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')
    else:
        query = request.GET['query']
        pessoa_filter = request.GET.getlist('pessoa', [])
        municipio_filter = request.GET.getlist('municipio', [])
        organizacao_filter = request.GET.getlist('organizacao', [])
        local_filter = request.GET.getlist('local', [])

        if '_segmentado' in doc_type:
            # requisita a estrutura de navegação do documento, para criar um índice lateral na página
            nav_params = {
                'doc_type': doc_type, 
                'doc_id': doc_id, 
                'query':query,
                'pessoa_filter': pessoa_filter,
                'municipio_filter': municipio_filter,
                'organizacao_filter': organizacao_filter,
                'local_filter': local_filter,
                }
            nav_response = requests.get(settings.SERVICES_URL+'document_navigation', nav_params, headers=headers)
            navigation = nav_response.json()['navigation']

            response_content = service_response.json()
            context = {
                'user_name': request.session.get('user_info')['first_name'],
                'query': query,
                'document': response_content['document'],
                'navigation': navigation
            }
            return render(request, 'aduna/document_segmented.html', context)
        else:
            response_content = service_response.json()
            document = response_content['document']
            document['conteudo'] = document['conteudo'].replace('\n', '<br>')
            document['conteudo'] = re.sub('(<br>){3,}', '<br>', document['conteudo'])
            context = {
                'user_name': request.session.get('user_info')['first_name'],
                'document': document
            }
            return render(request, 'aduna/document.html', context)


def login(request):
    if request.method == 'GET':
        if request.session.get('auth_token'):
            return redirect('/aduna/')
        return render(request, 'aduna/login.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        service_response = requests.post(settings.SERVICES_URL+'login', {'username': username, 'password': password})
        if service_response.status_code == 401:
            messages.add_message(request, messages.ERROR, 'Usuário ou senha inválidos.', extra_tags='danger')
            return redirect('/aduna/login')
        else:
            response_content = service_response.json()
            request.session['user_info'] = response_content['user_info']
            request.session['auth_token'] = response_content['token']
            return redirect('/aduna/')
            


def logout(request):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}
    service_response = requests.post(settings.SERVICES_URL+'logout', headers=headers)

    messages.add_message(request, messages.INFO, 'Você saiu.', extra_tags='info')
    request.session['user_info'] = None
    request.session['auth_token'] = None
    return redirect('/aduna/login')

def erro(request):
    return render(request, 'aduna/erro.html')    


def search_comparison(request):
    if request.GET.get('invalid_query', False) or not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    sid = request.session.session_key
    query = request.GET.get('query', 'comparação de busca')
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    instances = request.GET.getlist('instance', [])
    doc_types = request.GET.getlist('doc_type', [])
    start_date = request.GET.get('start_date', None)
    if start_date == "":
        start_date = None
    end_date = request.GET.get('end_date', None)
    if end_date == "":
        end_date = None
    
    params = {
        'query': query, 
        'page': page, 
        'sid': sid, 
        'qid': qid, 
        'instances': instances, 
        'doc_types': doc_types,
        'start_date': start_date,
        'end_date': end_date
    }
    service_response = requests.get(settings.SERVICES_URL+'search_comparison', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')

    else:
        # Verificação dos ids de resposta
        id_pos = defaultdict(list)
        for result in response_content['documents']:
            id_pos[result['id']].append('{}: {}ª posição'.format(response_content['algorithm_base'], result['rank_number']))
        for result in response_content['documents_repl']:
            if id_pos[result['id']]:
                id_pos[result['id']].append('<br>')    
            id_pos[result['id']].append('{}: {}ª posição'.format(response_content['algorithm_repl'], result['rank_number']))

        id_pos = dict(id_pos) # Converte de volta pra dict, pois o Django Template Language não lê defaultdict
        for k, v in id_pos.items():
            id_pos[k] = ''.join(v)

        context = {
            'auth_token': request.session.get('auth_token'),
            'user_name': request.session.get('user_info')['first_name'],
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': response_content['time'],
            'qid': response_content['qid'],
            'total_docs': response_content['total_docs'],
            'results_per_page': range(response_content['results_per_page']),
            'documents': response_content['documents'],
            'total_pages': response_content['total_pages'],
            'results_pagination_bar': range(min(9, response_content['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
            'start_date': datetime.strptime(response_content['start_date'], '%Y-%m-%d') if response_content['start_date'] != None else None,
            'end_date': datetime.strptime(response_content['end_date'], '%Y-%m-%d') if response_content['end_date'] != None else None,
            'instances': response_content['instances'],
            'doc_types': response_content['doc_types'],
            'filter_instances': ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2','Obras TCE'],#TODO:Automatizar
            'filter_doc_types': ['Diario', 'Processo', 'Licitacao'], #TODO:Automatizar
            'total_docs_repl': response_content['total_docs_repl'],
            'total_pages_repl': response_content['total_pages_repl'],
            'documents_repl': response_content['documents_repl'],
            'response_time': response_content['response_time'],
            'response_time_repl': response_content['response_time_repl'],
            'algorithm_base': response_content['algorithm_base'],
            'algorithm_repl': response_content['algorithm_repl'],
            'id_pos': id_pos,
        }
        
        return render(request, 'aduna/search_comparison.html', context)


def search_comparison_entity(request):
    if request.GET.get('invalid_query', False) or not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    sid = request.session.session_key
    query = request.GET.get('query', 'comparação de busca com entidade')
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    instances = request.GET.getlist('instance', [])
    doc_types = request.GET.getlist('doc_type', [])
    start_date = request.GET.get('start_date', None)
    if start_date == "":
        start_date = None
    end_date = request.GET.get('end_date', None)
    if end_date == "":
        end_date = None
    
    params = {
        'query': query, 
        'page': page, 
        'sid': sid, 
        'qid': qid, 
        'instances': instances, 
        'doc_types': doc_types,
        'start_date': start_date,
        'end_date': end_date
    }
    service_response = requests.get(settings.SERVICES_URL+'search_comparison_entity', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')

    else:
        # Verificação dos ids de resposta
        id_pos = defaultdict(list)
        for result in response_content['documents_entity']:
            id_pos[result['id']].append('Com entidades: {}ª posição'.format(result['rank_number']))
        for result in response_content['documents']:
            if id_pos[result['id']]:
                id_pos[result['id']].append('<br>')    
            id_pos[result['id']].append('Sem entidades: {}ª posição'.format(result['rank_number']))

        print(id_pos)
        id_pos = dict(id_pos)
        for k, v in id_pos.items():
            id_pos[k] = ''.join(v)

        context = {
            'auth_token': request.session.get('auth_token'),
            'user_name': request.session.get('user_info')['first_name'],
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': response_content['time'],
            'qid': response_content['qid'],
            'total_docs': response_content['total_docs'],
            'results_per_page': range(response_content['results_per_page']),
            'documents': response_content['documents'],
            'total_pages': response_content['total_pages'],
            'results_pagination_bar': range(min(9, response_content['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
            'start_date': datetime.strptime(response_content['start_date'], '%Y-%m-%d') if response_content['start_date'] != None else None,
            'end_date': datetime.strptime(response_content['end_date'], '%Y-%m-%d') if response_content['end_date'] != None else None,
            'instances': response_content['instances'],
            'doc_types': response_content['doc_types'],
            'filter_instances': ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2','Obras TCE'],#TODO:Automatizar
            'filter_doc_types': ['Diario', 'Processo', 'Licitacao'],#TODO:Automatizar
            'total_docs_entity': response_content['total_docs_entity'],
            'total_pages_entity': response_content['total_pages_entity'],
            'documents_entity': response_content['documents_entity'],
            'response_time': response_content['response_time'],
            'response_time_entity': response_content['response_time_entity'],
            'algorithm': response_content['algorithm'],
            'entities': response_content['entities'],
            'id_pos': id_pos, # Converte de volta pra dict, pois o Django Template Language não lê defaultdict
        }
        print(response_content['entities'])
        
        return render(request, 'aduna/search_comparison_entity.html', context)