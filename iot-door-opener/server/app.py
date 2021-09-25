import os

from dotenv import load_dotenv
from starlette.applications import Starlette

from .routes import routes

load_dotenv()

app = Starlette(routes=routes, debug=True)
