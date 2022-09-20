from datetime import datetime

def get_current_timestamp() -> int:
    '''Retorna o timestamp atual em milisegundos.
    '''
    now = datetime.now()
    return round(now.timestamp() * 1000)