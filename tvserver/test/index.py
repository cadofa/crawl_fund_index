import tornado.web

from utils import url_prefix

@url_prefix(r"/testagain")
class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('testagain')
