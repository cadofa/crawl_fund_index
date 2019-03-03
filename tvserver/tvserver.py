import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

#from test.login import url_pattern
#from test.index import url_pattern
#from test.crawl import url_pattern
import test.login
import test.index
import test.crawl
from test.utils import url_pattern

print url_pattern

define("port", default=8000, help="run on the given port", type=int)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(url_pattern, debug=True, gzip=True)
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)
    #application.listen(options.port)
    #server.bind(options.port)
    #server.start(1)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
