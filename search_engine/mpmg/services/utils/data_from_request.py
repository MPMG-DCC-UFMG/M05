from rest_framework.request import Request

def get_data_from_request(request: Request) -> dict:
    try:
        data = request.data.dict()
    
    except:
        data = request.data 

    return data