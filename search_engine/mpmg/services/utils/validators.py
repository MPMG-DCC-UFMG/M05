from typing import Tuple


def all_expected_fields_are_available(data: dict, expected_fields: set) -> Tuple[bool, list]:
    data_fields = set(data.keys())
    
    diff_expected_fields = expected_fields.difference(data_fields)
    if len(diff_expected_fields) > 0:
        return False, 'O(s) seguinte(s) campo(s) precisa(m) ser informado(s): ' + ', '.join(diff_expected_fields) + '.'

    return True, '' 


def some_expected_fields_are_available(data: dict, valid_fields: set) -> Tuple[bool, list]:
    data_fields = set(data.keys())
    
    not_valid_fields = data_fields.difference(valid_fields)
    if not_valid_fields:
        return False, 'Os seguintes campos são inválidos: ' + ', '.join(not_valid_fields) + '.'

    intersection_valid_fields = valid_fields.intersection(data_fields)
    if len(intersection_valid_fields) == 0:
        return False, 'Alguns dos seguintes campos precisam ser informados: ' + ', '.join(valid_fields) + '.'

    return True, '' 