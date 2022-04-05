from datetime import datetime, date
from mpmg.services.models.elastic_model import ElasticModel


class LogSearchClick(ElasticModel):
    index_name = 'log_clicks'

    def __init__(self, **kwargs):
        index_name = LogSearchClick.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'id_documento',
            'id_consulta',
            'posicao',
            'data_criacao',
            'tipo_documento',
            'pagina',
        ]
    
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    
    @staticmethod
    def get_list_filtered(id_documento=None, tipo_documento=None, id_consulta=None, start_date=None, end_date=None, pagina_op=None, pagina=None, posicao_op=None, posicao=None, id_consultas=None, page='all', sort=None):
        query_param = {
            "bool": {
                "must": []
            }
        }

        if id_consultas:
            query_param["bool"]["must"].append({
                "terms": {
                    "id_consulta.keyword": id_consultas
                }
            })
        

        if id_documento:
            query_param["bool"]["must"].append({
                "term": {
                    "id_documento": id_documento

                }
            })
        
        if tipo_documento:
            query_param["bool"]["must"].append({
                "term": {
                    "tipo_documento": tipo_documento

                }
            })
        
        if id_consulta:
            query_param["bool"]["must"].append({
                "term": {
                    "id_consulta": id_consulta

                }
            })
        
        if start_date:
            if type(start_date) == str: # de string para datetime
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
    
            if type(start_date) == datetime or type(start_date) == date: # de datetime para milisegundos
                start_date = int(datetime(year=start_date.year, month=start_date.month, day=start_date.day).timestamp() * 1000)

            query_param["bool"]["must"].append({
                "range": {
                    "data_criacao": {
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
                    "data_criacao": {
                        "lte": end_date
                    }
                }
            })
        
        if pagina and pagina_op:
            if pagina_op == 'e':
                    query_param["bool"]["must"].append({
                    "term": {
                        "pagina": pagina
                    }
                })
            else:
                query_param["bool"]["must"].append({
                    "range": {
                        "pagina": {
                            pagina_op: pagina
                        }
                    }
                })

        if posicao and posicao_op:
            if posicao_op == 'e':
                    query_param["bool"]["must"].append({
                    "term": {
                        "posicao": posicao
                    }
                })
            else:
                query_param["bool"]["must"].append({
                    "range": {
                        "posicao": {
                            posicao_op: posicao
                        }
                    }
                })
        
        return LogSearchClick.get_list(query=query_param, page=page, sort=sort)