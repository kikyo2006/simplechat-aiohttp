import os
import jinja2
from aiohttp import web
import aiohttp_jinja2 as jtemplate
from routes import routes

PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(PROJECT_APP_PATH, "templates")
STATIC_PATH = os.path.join(PROJECT_APP_PATH, "static")
MEDIA_PATH = os.path.join(PROJECT_APP_PATH, "media")

app = web.Application()
app.add_routes(routes)
app.router.add_static('/static', STATIC_PATH, name='static')
app.router.add_static('/media', MEDIA_PATH, name='media')
jtemplate.setup(app, loader=jinja2.FileSystemLoader(TEMPLATE_PATH))


if __name__ == '__main__':
    web.run_app(app)
