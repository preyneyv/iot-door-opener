from jwt import InvalidTokenError
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..helpers import get_token_from_request
from ..logging import logger
from ..jwt import decode_access_token

log = logger.getChild('Door')


def unlock(req: Request) -> JSONResponse:
    l = log.getChild('Unlock')
    try:
        token = get_token_from_request(req)
    except KeyError:
        return JSONResponse({
            'status': 'No token provided!'
        }, status_code=401)
    except AssertionError:
        return JSONResponse({
            'status': 'Invalid authentication type!'
        }, status_code=401)
    try:
        data = decode_access_token(token)
    except InvalidTokenError:
        l.error(f'Rejected. Invalid token. ({token})')
        return JSONResponse({
            'status': 'Invalid token!'
        }, status_code=401)

    name = data['name']
    l.info(f'Accepted. {name} opened the door.')
    return JSONResponse({
        'status': 'Opening!',
        'approved': True
    })