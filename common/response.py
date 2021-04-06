from fastapi.encoders import jsonable_encoder
from starlette.responses import UJSONResponse


def success_response(data=None, code=200):
    return UJSONResponse(status_code=code, content=jsonable_encoder({'status': 'success', 'data': data}))


def error_response(code=400, message=None, detail=None):
    response = {'code': code}
    if message:
        response['message'] = message
    if detail:
        response['detail'] = detail
    return UJSONResponse(status_code=code, content=jsonable_encoder({'status': 'error', 'error': response}))
