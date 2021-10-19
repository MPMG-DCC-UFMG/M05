from datetime import datetime, date
from mpmg.services.models.elastic_model import ElasticModel

class LogSearch(ElasticModel):
    index_name = 'log_buscas'

    def __init__(self, **kwargs):
        index_name = LogSearch.index_name
        meta_fields = ['id']
        index_fields = [
            'id_sessao',
            'id_consulta',
            'id_usuario',
            'text_consulta',
            'data_hora',
            'tempo_resposta',
            'tempo_resposta_total',
            'documentos',
            'pagina',
            'resultados_por_pagina',
            'indices',
            
            'algoritmo',
            'algoritmo_variaveis',

            'campos_ponderados'
            
            'instancias',
            'data_inicial',
            'data_final',
            'filtros'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    
    @staticmethod
    def get_list_filtered(id_sessao=None, id_consulta=None, id_usuario=None, text_consulta=None, algoritmo=None, start_date=None, end_date=None, page='all', tempo=None, tempo_op=None, sort=None):
        query_param = {
            "bool": {
                "must": []
            }
        }

        if id_sessao:
            query_param["bool"]["must"].append({
                "term": {
                    "id_sessao": id_sessao

                }
            })
        
        if id_consulta:
            query_param["bool"]["must"].append({
                "term": {
                    "id_consulta": id_consulta

                }
            })

        if id_usuario:
            query_param["bool"]["must"].append({
                "term": {
                    "id_usuario": id_usuario

                }
            })
        
        if text_consulta:
            query_param["bool"]["must"].append({
                "term": {
                    "text_consulta": text_consulta

                }
            })
        
        if algoritmo:
            query_param["bool"]["must"].append({
                "term": {
                    "algoritmo": algoritmo

                }
            })

        if start_date:
            if type(start_date) == str: # de string para datetime
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
            if type(start_date) == datetime or type(start_date) == date: # de datetime para milisegundos
                start_date = int(datetime(year=start_date.year, month=start_date.month, day=start_date.day).timestamp() * 1000)

            query_param["bool"]["must"].append({
                "range": {
                    "data_hora": {
                        "gte": start_date
                    }
                }
            })

        if end_date:
            if type(end_date) == str: # de string para datetime
                end_date = datetime.strptime(end_date, '%d/%m/%Y')
            if type(end_date) == datetime or type(end_date) == date: # de datetime para milisegundos
                end_date = int(datetime(year=end_date.year, month=end_date.month, day=end_date.day).timestamp() * 1000)

            query_param["bool"]["must"].append({
                "range": {
                    "data_hora": {
                        "lte": end_date
                    }
                }
            })
        
        if tempo and tempo_op:
            if tempo_op == 'e':
                    query_param["bool"]["must"].append({
                    "term": {
                        "tempo_resposta_total": tempo
                    }
                })
            else:
                query_param["bool"]["must"].append({
                    "range": {
                        "tempo_resposta_total": {
                            tempo_op: tempo
                        }
                    }
                })

        return LogSearch.get_list(query=query_param, page=page, sort=sort)

    @staticmethod
    def get_suggestions(query):
        request_body = {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "text_consulta",
                    "text_consulta._2gram",
                    "text_consulta._3gram"
                ]
            }
        }
        response = LogSearch.get_list(query=request_body, page='all')
        total = response[0]
        suggestions = [ hit['text_consulta'] for hit in response[1]]
        return total, suggestions