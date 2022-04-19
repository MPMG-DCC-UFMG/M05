from mpmg.services.elastic import Elastic

ELASTIC = Elastic()

def doc_filter(index_name: str, filter: dict) -> list:
    ''' Filtra documentos do índice index_name conforme o filtro filter passado.

    Args:
        - index_name: Índice a ter documentos filtrados.
        - filter: Filtro a ser aplicado aos documentos do índice.

    Returns:
        Retorna uma lista de documentos que passaram pelo filtro.
        
    '''
    
    elastic_result = ELASTIC.dsl.Search(using=ELASTIC.es, index=index_name) \
    .filter(filter) \
    .execute() \
    .to_dict()
    
    return elastic_result['hits']['hits']