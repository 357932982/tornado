# coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import hashlib

tornado.options.define("port", default=8000, type=int)

TOKEN = "xiaoming"


class WeiChatHandler(tornado.web.RequestHandler):
    def get(self):
        """"开发者验证接口"""
        signature = self.get_argument("signature", "")
        timestamp = self.get_argument("timestamp", "")
        nonce = self.get_argument("nonce", "")
        echostr = self.get_argument("echostr", "")
        tmp = [TOKEN, timestamp, nonce]
        tmp.sort()
        tmp = "".join(tmp)
        tmp = hashlib.sha1(tmp).hexdigest()
        if tmp == signature:
            self.write(echostr)
        else:
            self.write("error")


def main():
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", WeiChatHandler),
    ],
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
