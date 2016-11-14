import tornado.web

from utils import url_prefix, url_pattern

url_pattern = url_pattern

@url_prefix(r"/testagain")
class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('testagain')