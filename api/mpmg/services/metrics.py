from cgi import print_arguments
import math
import numpy as np
import pandas as pd
import time
from datetime import datetime
import requests
from collections import defaultdict
from mpmg.services.models import LogSearch, LogSearchClick, LogSugestoes


class Metrics:
    def __init__(self, api_client_name, start_date=None, end_date=None):
        self.api_client_name = api_client_name
        self.start_date = start_date 
        self.end_date = end_date
        self.query_log, self.click_log, self.sugestion_log = self._get_logs()
        

    def _get_logs(self):
        _, query_log = LogSearch.get_list_filtered(self.api_client_name, start_date=self.start_date, end_date=self.end_date)
        query_log = pd.DataFrame.from_dict(query_log)
        
        _, sugestion_log = LogSugestoes.get_list_filtered(self.api_client_name, start_date=self.start_date, end_date=self.end_date)
        sugestion_log = pd.DataFrame.from_dict(sugestion_log)

        # create columns to help on grouping
        if len(query_log) > 0:
            query_log['dia'] = query_log['data_criacao'].apply(lambda v: datetime.fromtimestamp(v/1000).date().strftime('%d/%m'))

            id_consultas = query_log['id_consulta'].to_list()

            _, click_log = LogSearchClick.get_list_filtered(self.api_client_name, id_consultas=id_consultas)
            click_log = pd.DataFrame.from_dict(click_log)
            
            if len(click_log) > 0:
                click_log['dia'] = click_log['data_criacao'].apply(lambda v: datetime.fromtimestamp(v/1000).date().strftime('%d/%m'))
                click_log['posicao'] = pd.to_numeric(click_log['posicao']) 
            else:
                click_log = pd.DataFrame(columns=LogSearchClick().index_fields+['dia'])

        else:
            click_log = pd.DataFrame(columns=LogSearchClick().index_fields+['dia'])


        query_log.rename(columns={'data_criacao': 'query_log_data_criacao'}, inplace=True)
        click_log.rename(columns={'data_criacao': 'click_log_data_criacao'}, inplace=True)
        sugestion_log.rename(columns={'data_criacao': 'sugestion_log_data_criacao'}, inplace=True)

        return query_log, click_log, sugestion_log
    

    def no_clicks_query(self):
        # consultas com resultado, mas sem nenhum click
        unclicked_queries = []
        for i,q in self.query_log.iterrows():
            if len(q['documentos']) > 0:
                if len(self.click_log) > 0 and q['id_consulta'] not in self.click_log['id_consulta'].to_list():
                    unclicked_queries.append(q.to_dict())
        response = {
            "no_clicks_query": len(unclicked_queries),
            "detailed": unclicked_queries
        }
        return response

    def no_results_query(self):
        #consultas sem nenhum resultado, ou seja,
        #consultas em que a pagina é igual a 1 e a lista de documentos esta vazia
        if len(self.query_log) > 0:
            no_ressults = self.query_log.loc[ (self.query_log['pagina'] == 1) & (self.query_log['documentos'].str.len() == 0) ]
            no_ressults = no_ressults.reset_index(drop=True)
        else:
            no_ressults = pd.DataFrame.from_dict({})
        response = {
            "no_results_query":len(no_ressults),
            "detailed": no_ressults.to_dict(orient='records')
        }
        return response

    def avg_click_position(self):
        #media da posição dos clicks
        df = pd.DataFrame(self.click_log['posicao'].astype(int))
        response = {
            "avg_click_position": self.click_log['posicao'].astype(int).mean() if len(self.click_log) > 0 else [],
            "avg_click_position_per_day": self.click_log.groupby(by='dia').mean()['posicao'].to_dict() if len(self.click_log) > 0 else []
        }
        return response

    def clicks_per_document(self):
        #clicks por documento for every recovered document
        recovered_docs = []
        for docs in self.query_log['documentos']:
            recovered_docs = recovered_docs + docs
        recovered_docs = pd.Series(recovered_docs).drop_duplicates().to_list()

        data = []
        for doc in recovered_docs:
            d = {
                "id_documento": doc
            }
            d["n_clicks"] = len(self.click_log[self.click_log['id_documento'] == doc])
            data.append(d)
            
        response = {
            "clicks_per_document": data
        }
        return response

    def clicks_per_position(self):
        #clicks por posição
        data = {
            "clicks_per_position": self.click_log.groupby(by='posicao', as_index=False ).count()[['posicao','id_documento']].to_dict(orient='records')
        }
        return data
    

    def avg_clicks_per_query(self):
        if len(self.query_log) > 0:
            query_ids = self.query_log['id_consulta'].unique()
        else:
            query_ids = []

        if len(self.click_log) > 0:
            valid_clicks = self.click_log['id_consulta'].isin(query_ids)
            df_count = self.click_log[valid_clicks].groupby(by=['id_consulta', 'dia']).count().reset_index()
            df_count = df_count[['id_consulta', 'dia', 'id']].rename(columns={'id':'count'})
            
            avg_clicks_per_query_by_day = df_count.groupby(by='dia').mean().reset_index().rename(columns={'count':'mean'})
            return {'avg_clicks_per_query_by_day': avg_clicks_per_query_by_day.to_dict(orient='records')}
        else:
            return {'avg_clicks_per_query_by_day': {}}
    

    def avg_session_duration(self):
        avg_session_duration_by_day = {}
        if len(self.query_log) > 0:
            joint_df = self.query_log.set_index('id_consulta').join(self.click_log.set_index('id_consulta'), lsuffix='_query', rsuffix='_click')
            joint_df = joint_df.reset_index()
            joint_df = joint_df[['id_sessao', 'id_consulta', 'query_log_data_criacao', 'click_log_data_criacao', 'dia_query']]
            
            durations_by_date = defaultdict(list)    
            session_ids = joint_df['id_sessao'].unique()
            for s in session_ids:
                # A última interação do usuário na sessão pode ter sido a execução de uma consulta ou o clique em um link.
                # Por isso começo olhando a data da primeira consulta como início de sessão e pego a interação mais antiga 
                # como data de fim de sessão, que pode estar no log de consulta ou no log de click
                target_records = joint_df[joint_df['id_sessao'] == s]
                target_records = target_records.sort_values(by=['query_log_data_criacao', 'click_log_data_criacao']).reset_index(drop=True)

                dia = target_records['dia_query'][0]
                start_timestamp = target_records.iloc[0]['query_log_data_criacao']
                end_query_timestamp = target_records.iloc[-1]['query_log_data_criacao']
                end_click_timestamp = target_records.iloc[-1]['click_log_data_criacao']

                if start_timestamp == end_query_timestamp and math.isnan(end_click_timestamp):
                    # Não consigo ter uma data de fim de sessão nos casos em que o usuário fez uma consulta e não fez mais nada.
                    continue
                else:
                    end_timestamp = end_click_timestamp if end_click_timestamp > end_query_timestamp else end_query_timestamp
                    duration = int((end_timestamp - start_timestamp) / 1000)
                    durations_by_date[dia].append(duration)
                
            # faz a média de cada dia
            for day, durations in durations_by_date.items():
                avg_session_duration_by_day[day] = int(np.mean(durations))
            
            
        return avg_session_duration_by_day
        





    def avg_response_time(self):
        #calcula o tempo de resposta medio geral e o tempo de resposta medio para cada tamanho de consulta para cada algoritimo usado
        #alem de retornar o tempo medio geral, para cada tamanho de query retorna o tempo medio da busca e o numero de consultas para aquele tamanho
        df = pd.DataFrame(self.query_log)
        df['numero_termos'] = df['text_consulta'].apply(lambda x: len(x.replace('"', "").split(" ")))
        avg_times = df.groupby(by = ["algoritmo", "numero_termos", ], as_index =False)["tempo_resposta"].mean()
        response = {
            "avg_response_time": df["tempo_resposta"].astype(int).mean(),
            "detailed": avg_times.to_dict(orient='records')
        }
        return response

    def avg_time_to_first_click(self):
        #Calcula o tempo medio ate o primeiro click
        if len(self.query_log) > 0:
            queries = self.query_log['id_consulta'].drop_duplicates().to_list() #calcular todas as queries
        else:
            queries = {}
        
        times_by_date = defaultdict(list)
        times = []
        for q in queries:
            target_queries = self.query_log[self.query_log['id_consulta'] == q]
            target_queries = target_queries.sort_values(by='query_log_data_criacao').reset_index(drop=True)
            dia = target_queries['dia'][0]
            first_query = target_queries['query_log_data_criacao'][0]

            if len(self.click_log) > 0:
                if q in self.click_log["id_consulta"].to_list():
                    clicks = self.click_log[self.click_log['id_consulta'] == q]
                    clicks = clicks.sort_values(by='click_log_data_criacao', ).reset_index(drop=True)
                    first_click = clicks['click_log_data_criacao'][0]

                    time_to_click = first_click - first_query
                    times.append(time_to_click)
                    times_by_date[dia].append(time_to_click)
        
        
        for k,v in times_by_date.items():
            times_by_date[k] = pd.Series(v).astype(int).mean()
                
        
        response = {
            "avg_time_to_first_click": pd.Series(times).astype(int).mean(),
            "avg_time_to_first_click_by_date": times_by_date,
        }

        return response

    def avg_sugestions_click_position(self):
        #media da posição dos clicks das sugestoes
        response = {
            "avg_sugestions_click_position": self.sugestion_log['posicao'].astype(int).mean()
        }
        return response
    
    def clicks_per_sugestion(self):

        sugestions = self.sugestion_log[['sugestao', 'id']].groupby(by='sugestao', as_index = False).count().rename(index=str,columns={'id':'clicks'})

        response = {
            "clicks_per_sugestion": sugestions.to_dict(orient='records')
        }
        return response

    

   