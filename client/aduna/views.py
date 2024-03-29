import re
import requests
import time
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from collections import defaultdict
from django.contrib.auth import authenticate, login as django_login, logout as django_logout

ENTITY_ICONS = {
    'entidade_pessoa': 'person',
    'entidade_municipio': 'location_city',
    'entidade_processo_licitacao': '',
    'entidade_jurisprudencia': '',
    'entidade_local': 'place',
    'entidade_organizacao': 'business',
    'entidade_cpf': '',
    'entidade_cnpj': '',
    'entidade_cep': '',
    'entidade_legislacao': 'gavel',
    'entidade_tempo': 'today',
} 


CTRL_SYMBOLS_REGEX = re.compile(r'[\n\r\t]')

def index(request):
    if not request.user.is_authenticated:
        return redirect('/aduna/login')
    
    context = {
        'api_client_name': request.user.api_client_name,
        'user_id': request.user.id,
        'user_name': request.user.username,
        'services_url': settings.SERVICES_URL,
    }
    
    return render(request, 'aduna/index.html', context)


def search(request):
    if request.GET.get('invalid_query', False) or not request.user.is_authenticated:
        return redirect('/aduna/login')
    
    headers = {} # headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    api_client_name = request.user.api_client_name
    sid = request.session.session_key
    query = request.GET['consulta']
    sort_order = request.GET.get('ordenacao', 'descendente')
    sort_by = request.GET.get('tipo_ordenacao', 'relevancia')
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('pagina', 1))
    
    # filtros em comum a todos --------------------------------------------
    filter_doc_types = request.GET.getlist('filtro_tipos_documentos', [])
    
    filter_start_date = request.GET.get('filtro_data_inicio', None)
    if filter_start_date == "":
        filter_start_date = None
    
    filter_end_date = request.GET.get('filtro_data_fim', None)
    if filter_end_date == "":
        filter_end_date = None
    
    
    # filtros da GSI -------------------------------------------------------
    filter_instances = request.GET.getlist('filtro_instancias', [])

    
    # filtros PROCON -------------------------------------------------------
    filter_city = request.GET.get('filtro_cidade') 
    filter_state = request.GET.get('filtro_estado')
    filter_business_category = request.GET.getlist('filtro_categoria_empresa', [])

    # filtros de entidades -------------------------------------------------
    filter_entidade_pessoa = request.GET.getlist('filtro_entidade_pessoa', [])
    filter_entidade_municipio = request.GET.getlist('filtro_entidade_municipio', [])
    filter_entidade_organizacao = request.GET.getlist('filtro_entidade_organizacao', [])
    filter_entidade_local = request.GET.getlist('filtro_entidade_local', [])

    # busca as opções do filtro
    params = {
        'consulta': query, 
        'filtro_instancias': filter_instances, 
        'filtro_tipos_documentos': filter_doc_types,
        'filtro_data_inicio': filter_start_date,
        'filtro_data_fim': filter_end_date,
        'filtro_entidade_pessoa': filter_entidade_pessoa,
        'filtro_entidade_municipio': filter_entidade_municipio,
        'filtro_entidade_organizacao': filter_entidade_organizacao,
        'filtro_entidade_local': filter_entidade_local,
    }

    # busca as opções de filtros gerais
    filter_response = requests.get(settings.SERVICES_URL+api_client_name+'/search_filter/all', headers=headers)
    filter_content = filter_response.json()
    filter_instances_list = filter_content['instances'] if 'instances' in filter_content else []
    filter_doc_types_list = filter_content['doc_types'] if 'doc_types' in filter_content else []

    if api_client_name == 'gsi':
        params['contexto'] = 'ranking'
        card_ranking_entities = requests.get(settings.SERVICES_URL+api_client_name+'/search_entities', params, headers=headers)
        card_ranking_entities = card_ranking_entities.json()
        
        # Se pelo menos um tipo de entidade teve recomendações de entidades, mostrar o card na interface
        at_least_one_entity_type_has_recommendations = False
        
        for entity_name, entity_vals in card_ranking_entities.items():
            entity_vals['icone'] = ENTITY_ICONS[entity_name]
            if len(entity_vals['ranking']) > 0:
                at_least_one_entity_type_has_recommendations = True

        # busca entidades além de buscar a consulta
        params['contexto'] = 'filtro'
        entities_list = requests.get(settings.SERVICES_URL+api_client_name+'/search_entities', params, headers=headers)
        entities_list = entities_list.json()
    
    else:
        at_least_one_entity_type_has_recommendations = False
        card_ranking_entities = []
        entities_list = []

    # faz a busca
    params = {
        'consulta': query, 
        'pagina': page, 
        'sid': sid, 
        'qid': qid, 
        'ordenacao': sort_order,
        'tipo_ordenacao': sort_by,
        'filtro_instancias': filter_instances, 
        'filtro_tipos_documentos': filter_doc_types,
        'filtro_data_inicio': filter_start_date,
        'filtro_data_fim': filter_end_date,
        'filtro_entidade_pessoa': filter_entidade_pessoa,
        'filtro_entidade_municipio': filter_entidade_municipio,
        'filtro_entidade_organizacao': filter_entidade_organizacao,
        'filtro_entidade_local': filter_entidade_local,
        'filtro_cidade': filter_city,
        'filtro_estado': filter_state,
        'filtro_categoria_empresa': filter_business_category
    }

    service_response = requests.get(settings.SERVICES_URL+api_client_name+'/search', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        return redirect('/aduna/login')

    else:
        # criar automaticamente o filter_urls a partir de params
        ignore_keys = {'consulta', 'pagina', 'sid', 'qid'}

        filter_url = ''
        for key, val in params.items():
            if key in ignore_keys:
                continue

            filter_item = f'&{key}='
            if type(val) is list:
                filter_url += filter_item + filter_item.join(val)

            else:
                filter_url += filter_item + val if val else filter_item 

        states = requests.get(settings.SERVICES_URL + 'states').json() if api_client_name == 'procon' else None
        cities = requests.get(settings.SERVICES_URL + f'cities?filtro_sigla_estado={filter_state}').json() if filter_state else None
        ra_business_categories = requests.get(settings.SERVICES_URL + 'reclame_aqui_business_categories').json() if api_client_name == 'procon' else None

        context = {
            'api_client_name': api_client_name,
            'user_name': request.user.username,
            'user_id': request.user.id,
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': response_content['time'],
            'qid': response_content['qid'],
            'total_docs': response_content['total_documentos'],
            'results_per_page': range(response_content['resultados_por_pagina']),
            'documents': response_content['documentos'],
            'total_pages': response_content['total_paginas'],
            'results_pagination_bar': range(min(9, response_content['total_paginas'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
            'entities_list': entities_list,
            'card_ranking_entities': card_ranking_entities,
            'at_least_one_entity_type_has_recommendations': at_least_one_entity_type_has_recommendations,
            'filter_start_date': datetime.strptime(response_content['filtro_data_inicio'], '%Y-%m-%d') if response_content['filtro_data_inicio'] != None else None,
            'filter_end_date': datetime.strptime(response_content['filtro_data_fim'], '%Y-%m-%d') if response_content['filtro_data_fim'] != None else None,
            'filter_instances': response_content['filtro_instancias'],
            'filter_doc_types': response_content['filtro_tipos_documentos'],
            'filter_instances_list': filter_instances_list,
            'filter_doc_types_list': filter_doc_types_list,
            'filter_entidade_pessoa': filter_entidade_pessoa,
            'filter_entidade_municipio': filter_entidade_municipio,
            'filter_entidade_organizacao': filter_entidade_organizacao,
            'filter_entidade_local': filter_entidade_local,
            'filter_url': filter_url,
            'filter_city': filter_city,
            'filter_state': filter_state,
            'filter_business_category': filter_business_category,  
            'states': states,
            'cities': cities,
            'ra_business_categories': ra_business_categories,
        }
        
        return render(request, 'aduna/search.html', context)
    

def document(request, tipo_documento, id_documento):
    if not request.user.is_authenticated:
        return redirect('/aduna/login')
    
    api_client_name = request.user.api_client_name

    headers = {} # headers = {'Authorization': 'Token '+request.session.get('auth_token')}
    sid = request.session.session_key
    service_response = requests.get(settings.SERVICES_URL+api_client_name+'/document', {'tipo_documento': tipo_documento, 'id_documento': id_documento}, headers=headers)

    if service_response.status_code == 401:
        return redirect('/aduna/')
    else:
        query = request.GET.get('query', '')
        pessoa_filter = request.GET.getlist('pessoa', [])
        municipio_filter = request.GET.getlist('municipio', [])
        organizacao_filter = request.GET.getlist('organizacao', [])
        local_filter = request.GET.getlist('local', [])

        if tipo_documento == 'diarios_segmentado':
            # requisita a estrutura de navegação do documento, para criar um índice lateral na página
            nav_params = {
                'tipo_documento': tipo_documento, 
                'id_documento': id_documento, 
                'consulta':query,
                'filtro_entidade_pessoa': pessoa_filter,
                'filtro_entidade_municipio': municipio_filter,
                'filtro_entidade_organizacao': organizacao_filter,
                'filtro_local': local_filter,
                }
            nav_response = requests.get(settings.SERVICES_URL+api_client_name+'/document_navigation', nav_params, headers=headers)
            navigation = nav_response.json()['navigation']

            response_content = service_response.json()
            document = response_content['document']

            document['titulo'] = CTRL_SYMBOLS_REGEX.sub(' ', document['titulo'])

            context = {
                'api_client_name': api_client_name,
                'services_url': settings.SERVICES_URL,
                'user_name': request.user.username,
                'query': query,
                'document': document,
                'navigation': navigation,
                'doc_type': tipo_documento,
                'doc_id': id_documento,
                'user_id': request.user.id,
            }
            return render(request, 'aduna/document_diario_segmentado.html', context)
        
        elif tipo_documento == 'reclame_aqui':
            response_content = service_response.json()
            document = response_content['document']

            document['titulo'] = CTRL_SYMBOLS_REGEX.sub(' ', document['titulo'])

            for i, seg in enumerate(document['segmentos']):
                document['segmentos'][i]['conteudo'] = seg['conteudo'].replace('\n', '<br>')

            context = {
                'api_client_name': api_client_name,
                'services_url': settings.SERVICES_URL,
                'user_name': request.user.username,
                'document': document,
                'query': query,
                'doc_type': tipo_documento,
                'doc_id': id_documento,
                'user_id': request.user.id,
            }
            return render(request, 'aduna/document_reclame_aqui.html', context)
        
        elif tipo_documento == 'consumidor_gov':
            response_content = service_response.json()
            document = response_content['document']

            document['titulo'] = CTRL_SYMBOLS_REGEX.sub(' ', document['titulo'])
            
            for i, seg in enumerate(document['segmentos']):
                document['segmentos'][i]['conteudo'] = seg['conteudo'].replace('\n', '<br>')

            context = {
                'api_client_name': api_client_name,
                'services_url': settings.SERVICES_URL,
                'user_name': request.user.username,
                'document': document,
                'query': query,
                'doc_type': tipo_documento,
                'doc_id': id_documento,
                'user_id': request.user.id,
            }
            return render(request, 'aduna/document_consumidor_gov.html', context)

        else:
            response_content = service_response.json()
            document = response_content['document']

            document['titulo'] = CTRL_SYMBOLS_REGEX.sub(' ', document['titulo'])
            document['conteudo'] = document['conteudo'].replace('\n', '<br>')
            document['conteudo'] = re.sub('(<br>){3,}', '<br>', document['conteudo'])

            context = {
                'api_client_name': api_client_name,
                'services_url': settings.SERVICES_URL,
                'user_name': request.user.username,
                'document': document,
                'query': query,
                'doc_type': tipo_documento,
                'doc_id': id_documento,
                'user_id': request.user.id,
            }

            return render(request, 'aduna/document_default.html', context)

def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/aduna/')
        return render(request, 'aduna/login.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            return redirect('/aduna/')
        else:
            messages.add_message(request, messages.ERROR, 'Usuário ou senha inválidos.', extra_tags='danger')
            return redirect('/aduna/login')
            


def logout(request):
    if not request.user.is_authenticated:
        return redirect('/aduna/login')
    
    django_logout(request)

    messages.add_message(request, messages.INFO, 'Você saiu.', extra_tags='info')
    return redirect('/aduna/login')

def erro(request):
    return render(request, 'aduna/erro.html')    


def search_comparison(request):
    if request.GET.get('invalid_query', False) or not request.user.is_authenticated:
        return redirect('/aduna/login')

    headers = {} # headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    api_client_name = request.user.api_client_name
    sid = request.session.session_key
    query = request.GET.get('query', 'comparação de busca')
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    instances = request.GET.getlist('instance', [])
    tipo_documentos = request.GET.getlist('doc_type', [])
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
        'doc_types': tipo_documentos,
        'start_date': start_date,
        'end_date': end_date
    }
    service_response = requests.get(settings.SERVICES_URL+api_client_name+'/search_comparison', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        return redirect('/aduna/login')

    else:
        # Verificação dos ids de resposta
        id_pos = defaultdict(list)
        for result in response_content['documents']:
            id_pos[result['id']].append('{}: {}ª posição'.format(response_content['algorithm_base'], result['posicao_ranking']))
        for result in response_content['documents_repl']:
            if id_pos[result['id']]:
                id_pos[result['id']].append('<br>')    
            id_pos[result['id']].append('{}: {}ª posição'.format(response_content['algorithm_repl'], result['posicao_ranking']))

        id_pos = dict(id_pos) # Converte de volta pra dict, pois o Django Template Language não lê defaultdict
        for k, v in id_pos.items():
            id_pos[k] = ''.join(v)

        context = {
            'user_name': request.user.username,
            'user_id': request.user.id,
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
    if request.GET.get('invalid_query', False) or not request.user.is_authenticated:
        return redirect('/aduna/login')
    
    headers = {} # headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    api_client_name = request.user.api_client_name
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

    service_response = requests.get(settings.SERVICES_URL+api_client_name+'/search_comparison_entity', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        return redirect('/aduna/login')

    else:
        # Verificação dos ids de resposta
        id_pos = defaultdict(list)
        for result in response_content['documents_entity']:
            id_pos[result['id']].append('Com entidades: {}ª posição'.format(result['posicao_ranking']))
        for result in response_content['documents']:
            if id_pos[result['id']]:
                id_pos[result['id']].append('<br>')    
            id_pos[result['id']].append('Sem entidades: {}ª posição'.format(result['posicao_ranking']))

        id_pos = dict(id_pos)
        for k, v in id_pos.items():
            id_pos[k] = ''.join(v)

        context = {
            'user_id': request.user.id,
            'user_name': request.user.username,
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

        return render(request, 'aduna/search_comparison_entity.html', context)

def bookmark(request):
    if not request.user.is_authenticated:
        return redirect('/aduna/login')
    
    api_client_name = request.user.api_client_name

    context = {
        'api_client_name': api_client_name,
        'services_url': settings.SERVICES_URL,
        'user_id': request.user.id
    }
    
    return render(request, 'aduna/bookmark.html', context)


def recommendations(request):
    if not request.user.is_authenticated:
        return redirect('/aduna/login')

    api_client_name = request.user.api_client_name

    notification_id = request.GET.get('notification_id', '')
    if notification_id:
        # Informa que a notificação foi visualizada
        headers = {} # headers = {'Authorization': 'Token '+ request.session.get('auth_token')}
        service_response = requests.put(settings.SERVICES_URL+api_client_name+'/notification', 
                                        data={
                                            'id_notificacao': notification_id,
                                            'visualizado': True
                                        }, 
                                        headers=headers)

        # atrasa um pouco a resposta para que haja tempo de o ES atualize o index
        if service_response.status_code == 204:
            time.sleep(.5)

    ctx = {
        'user_id': request.user.id,
        'notification_id': notification_id,
        'api_client_name': api_client_name,
        'services_url': settings.SERVICES_URL
    }

    return render(request, 'aduna/recommendation.html', ctx)