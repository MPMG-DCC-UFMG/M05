from typing import Tuple


def all_expected_fields_are_available(data: dict, expected_fields: set, optional_fields: str = {}) -> Tuple[bool, list]:
    '''Método responsável por checar se todos os campos esperados que um dado vindo do usuário sejam válidos, bem como ele
    não tenha passado campos inválidos.

    Args:
        - data: Conteúdo passado pelo usuário atráves de um formulário.
        - expected_fields: Conjunto de campos que devem existir nos dados passados pelo usuário.
        - optional_field: Conjunto de campos válidos mas opcionais.
    
    Returns:
        Retorna uma tupla onde a primeira posição indica se os dados são válidos e a segunda posição um string informando, caso 
        o dado seja inválido, o motivo.

    '''
    
    data_fields = set(data.keys())

    invalid_fields = data_fields.difference(expected_fields).difference(optional_fields)
    if invalid_fields:
        return False, 'O(s) seguinte(s) campo(s) é/são inválido(s): ' + ', '.join(invalid_fields) + '.'

    diff_expected_fields = expected_fields.difference(data_fields)
    if len(diff_expected_fields) > 0:
        return False, 'O(s) seguinte(s) campo(s) precisa(m) ser informado(s): ' + ', '.join(diff_expected_fields) + '.'

    return True, '' 


def some_expected_fields_are_available(data: dict, valid_fields: set) -> Tuple[bool, list]:
    '''Método que checa se alguns ou todos campos válidos foram informados pelo usuário. Útil para o caso de atualização de um 
    documento e temos determinados campos que o usuário pode atualizar.

    Args:
        - data: Dados passados pelo usuário.
        - valid_fields: Conjunto com campos válidos que podem estar no dado passado pelo usuário.
    
    Returns:
        Retorna uma tupla onde a primeira posição indica se o dado passado pelo usuário é válido e a segunda posição, caso o dado seja
        inválido, a sua causa.
    '''
    
    data_fields = set(data.keys())
    
    not_valid_fields = data_fields.difference(valid_fields)
    if not_valid_fields:
        return False, 'Os seguintes campos são inválidos: ' + ', '.join(not_valid_fields) + '.'

    intersection_valid_fields = valid_fields.intersection(data_fields)
    if len(intersection_valid_fields) == 0:
        return False, 'Alguns dos seguintes campos precisam ser informados: ' + ', '.join(valid_fields) + '.'

    return True, '' 