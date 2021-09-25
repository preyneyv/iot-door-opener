import jwt

from .helpers import env

KEY = env('IDO_JWT_SECRET')


def _create_token(data):
    return jwt.encode(data, KEY, algorithm='HS256')


def create_access_token(username):
    """Create an access token with the purpose of authenticating the user."""
    return _create_token({'name': username, 'aud': 'urn:lock/access'})


def create_status_token(request_id):
    """Create a token to retrieve the status of a token request."""
    return _create_token({'id': request_id, 'aud': 'urn:token/status'})


def _decode_token(token, audience=''):
    return jwt.decode(token, KEY, audience=audience, algorithms=['HS256'])


def decode_access_token(token):
    return _decode_token(token, 'urn:lock/access')


def decode_status_token(token):
    return _decode_token(token, 'urn:token/status')
