# -*-coding: utf-8 -*-

import json
import tornado.web

from utils import url_prefix


@url_prefix(r"/")
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(u"Hello<br><br>嘻嘻")


@url_prefix(r"/login")
class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument('username')
        print(username)
        if username == 'username':
            res = u'1'
        else:
            res = u'0'
        data = {'testResult': res}
        self.write(json.dumps(data))


@url_prefix(r"/tokenlogin")
class TokenLoginHandler(tornado.web.RequestHandler):
    def get(self):
        token = self.get_argument('token')
        self.write({'testResult': token})

@url_prefix(r"/dispatch")
class DispatchHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('dispatch ok')


@url_prefix(r"/perfect")
class PerfectHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('perfect')

