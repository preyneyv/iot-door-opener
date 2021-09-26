from starlette.responses import PlainTextResponse


def ping(_):
    return PlainTextResponse('')
