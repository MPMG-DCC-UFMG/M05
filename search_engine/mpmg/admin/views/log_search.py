from datetime import datetime
from django.contrib import admin
from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import User
from mpmg.services.models import LogSearch, LogSearchClick

class LogSearchView(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(LogSearchView, self).__init__()
    
    def view_log_search(self, request):
        results_per_page = int(request.GET.get('results_per_page', self.results_per_page))
        id_sessao = request.GET.get('id_sessao', '')
        id_consulta = request.GET.get('id_consulta', '')
        id_usuario = request.GET.get('id_usuario', '')
        text_consulta = request.GET.get('texto_consulta', '')
        algoritmo = request.GET.get('algoritmo', '')
        page = int(request.GET.get('page', 1))
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        tempo = request.GET.get('tempo', '')
        tempo_op = request.GET.get('tempo_op')
        self.results_per_page = results_per_page
        
        LogSearch.results_per_page = self.results_per_page
        total_records, log_buscas_list = LogSearch.get_list_filtered(
            api_client_name=request.user.api_client_name,
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            algoritmo=algoritmo,
            page=page, 
            start_date=start_date,
            end_date=end_date,
            tempo=tempo,
            tempo_op=tempo_op,
            sort={'data_criacao':{'order':'desc'}}
        )

        total_pages = (total_records // self.results_per_page) + 1

        url_params = "&id_sessao=%s&id_consulta=%s&id_usuario=%s"\
                    "&text_consulta=%s&algoritmo=%s&start_date=%s"\
                    "&end_date=%s&tempo=%s&tempo_op=%s"\
                    % (id_sessao, id_consulta, id_usuario,\
                    text_consulta, algoritmo, start_date, end_date, tempo, tempo_op)

        context = dict(
            self.each_context(request), # admin template variables.
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            algoritmo=algoritmo,
            start_date=start_date,
            end_date=end_date,
            tempo=tempo,
            tempo_op=tempo_op,
            result_list=log_buscas_list,
            page=page,
            total_records=total_records,
            results_per_page=self.results_per_page,
            total_pages=total_pages,
            pagination_items=range(min(9, total_pages)),
            url_params=url_params,
        )
        
        return render(request, 'admin/log_search.html', context)
    

    def view_detail(self, request):
        id_sessao = request.GET['id_sessao']
        _, results_list = LogSearch.get_list_filtered(request.user.api_client_name, id_sessao=id_sessao)
        id_consultas = set()
        session_detail = {'id_sessao':'', 'id_usuario':'', 'nome_usuario':'', 'consultas':{}}
        for item in results_list:
            session_detail['id_sessao'] = item.id_sessao
            session_detail['id_usuario'] = item.id_usuario
            session_detail['nome_usuario'] = User.objects.get(id=item.id_usuario).first_name
            id_consultas.add(item.id_consulta)
            
            if item.id_consulta not in session_detail['consultas']:
                session_detail['consultas'][item.id_consulta] = {
                'texto_consulta': item.texto_consulta,
                'algoritmo': item.algoritmo,
                'resultados_por_pagina': int(item.resultados_por_pagina),
                'paginas': {}
                }
            session_detail['consultas'][item.id_consulta]['paginas'][str(item.pagina)] = {
                'data_criacao': (datetime.fromtimestamp(item.data_criacao/1000)).strftime("%d/%m/%Y %H:%M:%S"),
                'tempo_resposta_total': round(item.tempo_resposta_total, 2),
                'tipos': [d.split(':')[0] for d in item.documentos],
                'documentos': [d.split(':')[1] for d in item.documentos],
                'cliques': ['-'] * len(item.documentos)
            }
        
        _, click_results_list = LogSearchClick.get_list_filtered(request.user.api_client_name, id_consultas=list(id_consultas))
        for item in click_results_list:
            resultados_por_pagina = session_detail['consultas'][item.id_consulta]['resultados_por_pagina']
            posicao = int(item.posicao) - ((int(item.pagina)-1) * resultados_por_pagina) #desconta as páginas anteriores pra ter uma posição entre 1 a 10
            posicao = posicao - 1 # os índices do array começam no zero
            session_detail['consultas'][item.id_consulta]['paginas'][str(item.pagina)]['cliques'][posicao] = (datetime.fromtimestamp(item.data_criacao / 1000)).strftime("%H:%M:%S")

        context = dict(session_detail=session_detail)
        return JsonResponse(context)        
