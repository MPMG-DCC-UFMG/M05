from services.models.elastic_model import ElasticModel


class LogSugestoes(ElasticModel):
    index_name = 'log_sugestoes'

    def __init__(self, **kwargs):
        index_name = LogSugestoes.index_name
        meta_fields = ['id']
        index_fields = [
            'sugestao',
            'posicao',
            'data_criacao',
        ]
    
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    @staticmethod
    def get_suggestions(query):
        request_body = {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "sugestao",
                    "sugestao._2gram",
                    "sugestao._3gram"
                ]
            }
        }

        response = LogSugestoes.get_list(query=request_body, page='all')
        total = response[0]
        suggestions = [ hit['sugestao'] for hit in response[1]]

        return total, suggestions
    
    @staticmethod
    def get_list_filtered(api_client_name, start_date=None, end_date=None, sugestao=None, page='all'):
        query_param = {
            "bool": {
                "must": []
            }
        }
        
        if sugestao:
            query_param["bool"]["must"].append({
                "term": {
                    "text_consulta": sugestao

                }
            })

        if start_date:
            query_param["bool"]["must"].append({
                "range": {
                    "data_criacao": {
                        "gte": start_date
                    }
                }
            })

        if end_date:
            query_param["bool"]["must"].append({
                "range": {
                    "data_criacao": {
                        "lte": end_date
                    }
                }
            })

        client_filter = [
            {"term": { "nome_cliente_api": api_client_name}}
        ]

        return LogSugestoes.get_list(query=query_param, filter=client_filter, page=page)