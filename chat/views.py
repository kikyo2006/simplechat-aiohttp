from aiohttp import web
import aiohttp_jinja2

class homepage(web.View):
    @aiohttp_jinja2.template('chat/room.html')
    async def get(self):
        return {'content': 'welcome'}
