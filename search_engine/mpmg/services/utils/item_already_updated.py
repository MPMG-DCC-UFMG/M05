def item_already_updated(ref: dict, item: dict) -> bool:
    has_updated_fields = False 

    # se ao menos um campo a ser atualizado é diferente do atual 
    for field, value in item.items():
        if item[field] != value:
            has_updated_fields = True 
            break 
    
    return has_updated_fields