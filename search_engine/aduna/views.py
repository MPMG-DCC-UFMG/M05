from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import requests


def index(request):
    if not request.session.session_key:
        request.session.create()
    
    context = {
        'sid': request.session.session_key,
        'services_url': settings.SERVICES_URL,
    }
    return render(request, 'aduna/index.html', context)
    # return HttpResponse("Hello, world. You're at the polls index.")


def search(request):
    query = request.GET['query']
    sid = request.GET['sid']
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    

    service_response = requests.get(settings.SERVICES_URL+'search', {'query': query, 'page': page, 'sid': sid, 'qid': qid}).json()

    context = {
        'services_url': settings.SERVICES_URL,
        'query': query,
        'page': page,
        'sid': sid,
        'qid': service_response['qid'],
        'total_docs': service_response['total_docs'],
        'results_per_page': range(service_response['results_per_page']),
        'documents': service_response['documents'],
        'total_pages': service_response['total_pages'],
        'results_pagination_bar': range(min(9, service_response['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
    }
    
    return render(request, 'aduna/search.html', context)


def document(request, doc_type, doc_id):
    import re
    service_response = requests.get(settings.SERVICES_URL+'document', {'doc_type': doc_type, 'doc_id':doc_id}).json()
    document = service_response['document']
    
    document['text'] = document['text'].replace('\n', '<br>')
    document['text'] = re.sub('(<br>){3,}', '<br>', document['text'])

    context = {'document': document}
    return render(request, 'aduna/document.html', context)