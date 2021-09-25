from starlette.routing import Route

from . import views

routes = [
    Route('/', views.homepage),
]
