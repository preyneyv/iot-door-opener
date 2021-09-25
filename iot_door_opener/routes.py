from pathlib import Path

from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from .controllers import tokens

routes = [
    Mount('/tokens', routes=[
        Route('/request', tokens.request, methods=['POST']),
        Route('/status', tokens.status, methods=['GET']),
    ]),

    Mount('/', name='static',
          app=StaticFiles(directory=Path(__file__).parent.joinpath('static'),
                          html=True)),

]