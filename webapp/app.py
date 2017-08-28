#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

import logging;
logging.basicConfig(level=logging.INFO)
import asyncio
from aiohttp import web
import orm 
from model import Blog, User, Comment

def index(request):
    return web.Response(body=b'<h1>Hello</h1>', content_type='text/html')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info("server started at http://127.0.0.1:9000...")

    logging.info("just begin")
    await orm.create_pool(loop=loop, user='bugtree', password='bugtree', db='blog') 
    u = User(name='Jim', email='Jim@google.com', password='123', image='blank')
    await u.save()


    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()



