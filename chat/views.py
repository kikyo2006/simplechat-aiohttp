import json
import settings
from aiohttp import web, WSMsgType
from aiohttp_session import get_session
import aiohttp_jinja2
from time import time
from datetime import datetime
from .model import User, Message
from settings import log

history = []

def redirect(request, router_name):
    url = request.app.router[router_name].url_for()
    raise web.HTTPFound(url)

def set_session(session, user_data):
    session['user'] = user_data
    session['last_visit'] = time()

def convert_json(message):
    return json.dumps({'error': message})

async def load_msg():
    if not history:
        message = Message()
        messages = await message.load_msg()

        for msg in messages:
            history.append(
                {'time': datetime.strptime(msg[1], '%Y-%m-%d %H:%M:%S.%f'), 'user': msg[0], 'msg': msg[2]})

class Login(web.View):
    @aiohttp_jinja2.template('chat/login.html')
    async def get(self):
        session_user = await get_session(self.request)
        if session_user.get('user'):
            redirect(self.request, 'room_chat')
        return None

    async def post(self):
        data = await self.request.post()
        user = User()
        result = await user.login_user(data.get('username'), data.get('password'))
        if isinstance(result, tuple):
            session = await get_session(self.request)
            set_session(session, {'id': result[0], 'username': result[1]})

            await load_msg()

            redirect(self.request, 'room_chat')
        else:
            return web.Response(text="Can't login")

class CreateUser(web.View):
    @aiohttp_jinja2.template('chat/create_user.html')
    async def get(self):
        return None

    async def post(self):
        data = await self.request.post()

        user = User()
        post = {'username': data.get('username'),
                'password': data.get('password'),
                'email': data.get('email')}
        result = await user.create_user(data=post)
        if isinstance(result, tuple):
            session = await get_session(self.request)
            set_session(session, {'id': result[0], 'username': result[1]})

            await load_msg()

            redirect(self.request, 'room_chat')
        else:
            return web.Response(text="Can't register")

class Logout(web.View):

    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            del session['user']

        redirect(self.request, 'homepage')

class RoomChat(web.View):
    @aiohttp_jinja2.template('chat/room_chat.html')
    async def get(self):
        session = await get_session(self.request)
        if not session.get('user'):
            redirect(self.request, 'homepage')

        return {'messages': history}


class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        session = await get_session(self.request)
        message = Message()

        session_user = session.get('user')
        username = session_user.get('username')

        for _ws in self.request.app['websockets']:
            await _ws.send_str('%s joined' % username)

        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.type == WSMsgType.text:
                for _ws in self.request.app['websockets']:
                    time_chat = datetime.now()
                    if len(history) > settings.MAX_MSG:
                        del history[0]

                    history.append({'time': time_chat, 'user': username, 'msg': msg.data})
                    await message.save_msg(
                        {'user_id': session_user.get('id'), 'created_at': time_chat, 'msg': msg.data})
                    await _ws.send_str('(%s) %s' % (username, msg.data))

            elif msg.type == WSMsgType.error:
                log.debug('ws connection closed with exception %s' % ws.exception())

        self.request.app['websockets'].remove(ws)

        for _ws in self.request.app['websockets']:
            await _ws.send_str('%s disconected' % username)

        log.debug('websocket connection closed')

        return ws

