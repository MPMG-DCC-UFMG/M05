from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connections
import spacy

class PipelineDirectories(APIView):

    def get(self, request):
        filter_category = request.GET.get('filter_category', None)

        cursor = connections['crawlers'].cursor()
        cursor.execute("SELECT source_name, base_url, data_path FROM main_crawlrequest")
        rows = cursor.fetchall()
        
        nlp = spacy.load("pt_core_news_md")


        data = []
        i=0
        for row in rows:
            category = self._find_category(row[0])
            if category == 'Outro':
                continue
            
            if filter_category == None or category == filter_category:
                location = self._find_location(nlp, row[0])
                data.append({'category': category, 'data_path': row[2], 'location': location})
            
        return Response(data)
    

    def _find_category(self, source_name):
        if 'licitações' in source_name.lower() or \
        'licitação' in source_name.lower() or \
        'licitacoes' in source_name.lower() or \
        'licitaçoes' in source_name.lower() or \
        'licitacao' in source_name.lower():
            return 'Licitações'
        
        if 'contratos' in source_name.lower():
            return 'Contratos'
        
        if 'diários' in source_name.lower() or \
        'diário' in source_name.lower() or \
        'diarios' in source_name.lower() or \
        'diario' in source_name.lower():
            return 'Diários'
        
        if 'transparência' in source_name.lower() or \
        'transparencia' in source_name.lower():
            return 'Transparência'
        
        if 'orçamentária' in source_name.lower() or \
        'orçamentaria' in source_name.lower() or \
        'orcamentaria' in source_name.lower() or \
        'orcamentária' in source_name.lower():
            return 'Leis Orçamentárias'
        
        return 'Outro'
    
    def _find_location(self, nlp, source_name):
        doc = nlp(source_name)
        for ent in doc.ents:
            # print(ent.text, ent.label_)
            return ent.text
        return ''