from aiohttp import web
from chat.views import homepage

routes = [
    web.get('/', homepage)
]
