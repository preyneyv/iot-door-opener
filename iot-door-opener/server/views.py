from starlette.responses import PlainTextResponse


def homepage(request):
    return PlainTextResponse('Hello, world!')
