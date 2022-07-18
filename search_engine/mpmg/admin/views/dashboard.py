import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from accounts.models import User
from django.conf import settings
from mpmg.services.models import ElasticModel, SearchableIndicesConfigs
from mpmg.services.metrics import Metrics

class DashboardView(admin.AdminSite):

    def __init__(self):
        super(DashboardView, self).__init__()
    
    def view_dashboard(self, request):
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        if start_date != None and end_date != None:
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
            
        else:
            end_date = datetime.today().date() #+ timedelta(days=1)
            start_date = end_date - timedelta(days=14)
        
        # período das métricas e estatísticas
        start_date_millis = int(datetime(year=start_date.year, month=start_date.month, day=start_date.day).timestamp() * 1000)
        end_date_millis = int(datetime(year=end_date.year, month=end_date.month, day=end_date.day).timestamp() * 1000)
        days_labels = [d.strftime('%d/%m') for d in pd.date_range(start_date, end_date)]

        # métricas
        metrics = Metrics(start_date, end_date)

        # informação sobre os índices
        indices_info = ElasticModel.get_indices_info()

        # total de registros (considerando apenas os índices principais)
        total_records = 0
        searchable_indices = SearchableIndicesConfigs.get_searchable_indices(groups=['regular'])
        for item in indices_info:
            if item['index_name'] in searchable_indices:
                total_records += int(item['num_documents'])
        

        cluster_info = ElasticModel.get_cluster_info()
        store_size = round(cluster_info['indices']['store']['size_in_bytes'] /1024 /1024 /1024, 2)
        allocated_processors = cluster_info['nodes']['os']['allocated_processors']
        jvm_heap_size = int(cluster_info['nodes']['jvm']['mem']['heap_max_in_bytes'] /1024 /1024 /1024)


        # dados para o gráfico de pizza com a qtde de documentos por índice
        searchable_indices = list(SearchableIndicesConfigs.get_indices_list())
        colors = ['#ffcd56', # amarelo
                  '#6ac472', # verde
                  '#ff9f40', # laranja
                  '#36a2eb', # azul
                  '#ff6384'] # rosa
        colors = [
            '#f94144',
            '#f3722c',
            '#f8961e',
            '#f9c74f',
            '#90be6d',
            '#43aa8b',
            '#577590',
        ]
        indices_amounts = {'data':[], 'colors':[], 'labels':[]}
        for item in indices_info:
            if item['index_name'] in searchable_indices:
                indices_amounts['data'].append(item['num_documents'])
                indices_amounts['colors'].append(colors.pop())
                indices_amounts['labels'].append(item['index_name'])
        
        # tempo de resposta médio por dia
        if len(metrics.query_log) > 0:
            mean_response_time = metrics.query_log.groupby(by='dia')['tempo_resposta_total'].mean().round(2).to_dict()
        else:
            mean_response_time = {}
        response_time_per_day = dict.fromkeys(days_labels, 0)
        for k,v in mean_response_time.items():
            if k in response_time_per_day:
                response_time_per_day[k] = v
        
        
        # join com usuários no dataframe
        users = {}
        if len(metrics.query_log) > 0:
            user_ids = metrics.query_log.id_usuario.unique()
            for user in User.objects.filter(id__in=user_ids):
                users[user.id] = {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name}
            metrics.query_log['nome_usuario'] = metrics.query_log['id_usuario'].apply(lambda i: users[i]['first_name'] if i in users else '')
        else:
            user_ids = []
        
        # Buscas por dia
        if len(metrics.query_log) > 0:
            queries_list = metrics.query_log.fillna('-').sort_values(by='query_log_data_criacao', ascending=False).to_dict('records')

        else:
            queries_list = []

        total_queries_per_day = dict.fromkeys(days_labels, 0)
        for item in queries_list:
            d = item['dia']
            if d in total_queries_per_day:
                total_queries_per_day[d] += 1

        # Consultas sem clique por dia
        no_clicks = metrics.no_clicks_query()
        no_clicks_per_day = dict.fromkeys(days_labels, 0)
        for item in no_clicks['detailed']:
            d = item['dia']
            if d in no_clicks_per_day:
                no_clicks_per_day[d] += 1
        
        # Consultas sem resultado
        no_results = metrics.no_results_query()
        no_results_per_day = dict.fromkeys(days_labels, 0)
        for item in no_results['detailed']:
            d = item['dia']
            if d in no_results_per_day:
                no_results_per_day[d] += 1
        
        # porcentagem sem clique (por dia)
        porc_no_clicks_per_day = {}
        for d, v in no_clicks_per_day.items():
            if total_queries_per_day[d] != 0:
                porc_no_clicks_per_day[d] = round(v/total_queries_per_day[d]*100)
            else:
                porc_no_clicks_per_day[d] = 0
        
        # porcentagem sem resultado (por dia)
        porc_no_results_per_day = {}
        for d, v in no_results_per_day.items():
            if total_queries_per_day[d] != 0:
                porc_no_results_per_day[d] = round(v/total_queries_per_day[d]*100)
            else:
                porc_no_results_per_day[d] = 0
        

        #posição média dos cliques
        avg_click_position_dict = metrics.avg_click_position()['avg_click_position_per_day']
        avg_click_position_per_day = dict.fromkeys(days_labels, 0)
        if len(avg_click_position_dict) > 0:
            for d, v in avg_click_position_dict.items():
                if d in avg_click_position_per_day:
                    avg_click_position_per_day[d] = round(v, 2)
        
        avg_click_position = round(np.mean(list(avg_click_position_per_day.values())), 2)


        # tempo até o primeiro clique
        time_to_first_click_dict = metrics.avg_time_to_first_click()['avg_time_to_first_click_by_date']
        time_to_first_click_per_day = dict.fromkeys(days_labels, 0)
        if len(time_to_first_click_dict) > 0:
            for d, v in time_to_first_click_dict.items():
                if d in time_to_first_click_per_day:
                    time_to_first_click_per_day[d] = round(v/1000)
        
        avg_time_to_first_click = int(np.mean(list(time_to_first_click_per_day.values())))
        

        # cliques por consulta
        avg_clicks_per_query_dict = metrics.avg_clicks_per_query()['avg_clicks_per_query_by_day']
        avg_clicks_per_query_per_day = dict.fromkeys(days_labels, 0)
        if len(avg_clicks_per_query_dict) > 0:
            for item in avg_clicks_per_query_dict:
                d = item['dia']
                v = item['mean']
                if d in avg_clicks_per_query_per_day:
                    avg_clicks_per_query_per_day[d] = round(v, 2)
        
        avg_clicks_per_query = round(np.mean(list(avg_clicks_per_query_per_day.values())), 2)


        # tempo das sessões
        avg_session_duration_dict = metrics.avg_session_duration()
        avg_session_duration_per_day = dict.fromkeys(days_labels, 0)
        for day, mean in avg_session_duration_dict.items():
            if day in avg_session_duration_per_day:
                avg_session_duration_per_day[day] = mean
        
        avg_session_duration = int(np.mean(list(avg_session_duration_per_day.values())))


        
        # totais
        if len(metrics.query_log) > 0:
            total_queries = metrics.query_log.id.value_counts().sum()
            total_no_clicks = no_clicks['no_clicks_query']
            total_no_results = no_results['no_results_query']
            porc_total_no_clicks = int(total_no_clicks / total_queries * 100)
            porc_total_no_results = int(total_no_results / total_queries * 100)
            avg_query_time = round(metrics.query_log.tempo_resposta_total.mean(), 2)
        else:
            total_queries = 0
            total_no_clicks = 0
            total_no_results = 0
            porc_total_no_clicks = 0
            porc_total_no_results = 0
            avg_query_time = 0

        context = dict(
            self.each_context(request), # admin variables
            services_url= settings.SERVICES_URL,
            allocated_processors= allocated_processors,
            jvm_heap_size= jvm_heap_size,
            start_date= start_date.strftime('%d/%m/%Y'),
            end_date= end_date.strftime('%d/%m/%Y'),
            total_records= total_records,
            total_queries= total_queries,
            store_size= store_size,
            avg_query_time= avg_query_time,
            total_no_clicks= total_no_clicks,
            total_no_results= total_no_results,
            porc_total_no_clicks= porc_total_no_clicks,
            porc_total_no_results= porc_total_no_results,
            indices_info= indices_info,
            indices_amounts= indices_amounts,
            total_searches_per_day= {'labels': list(total_queries_per_day.keys()), 'data': list(total_queries_per_day.values())},
            response_time_per_day= {'labels': list(response_time_per_day.keys()), 'data': list(response_time_per_day.values())},
            last_queries= queries_list[:10],
            no_clicks_per_day= {'labels': list(no_clicks_per_day.keys()), 'data': list(no_clicks_per_day.values())},
            no_results_per_day= {'labels': list(no_results_per_day.keys()), 'data': list(no_results_per_day.values())},
            porc_no_clicks_per_day= {'labels': list(porc_no_clicks_per_day.keys()), 'data': list(porc_no_clicks_per_day.values())},
            porc_no_results_per_day= {'labels': list(porc_no_results_per_day.keys()), 'data': list(porc_no_results_per_day.values())},
            time_to_first_click_per_day= {'labels': list(time_to_first_click_per_day.keys()), 'data': list(time_to_first_click_per_day.values())},
            avg_time_to_first_click= avg_time_to_first_click,
            avg_click_position= avg_click_position,
            avg_click_position_per_day = {'labels':list(avg_click_position_per_day.keys()), 'data': list(avg_click_position_per_day.values())},
            avg_clicks_per_query= avg_clicks_per_query,
            avg_clicks_per_query_per_day = {'labels': list(avg_clicks_per_query_per_day.keys()), 'data': list(avg_clicks_per_query_per_day.values())},
            avg_session_duration = avg_session_duration,
            avg_session_duration_per_day = {'labels': list(avg_session_duration_per_day.keys()), 'data': list(avg_session_duration_per_day.values())},
        )
        return render(request, 'admin/index.html', context)
