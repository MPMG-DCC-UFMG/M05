def str2bool(s: str) -> bool:
    s = s.lower()

    if s in ('true', '1'):
        return True

    elif s in ('null', ''):
        return None
    
    else:
        return False