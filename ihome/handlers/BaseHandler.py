# coding=utf-8

from tornado.web import RequestHandler, StaticFileHandler


class BaseHandler(RequestHandler):
    """handler基类"""

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def prepare(self):
        pass

    def write_error(self, status_code, **kwargs):
        pass

    def set_default_headers(self):
        pass

    def initialize(self):
        pass

    def on_finish(self):
        pass


class StaticFileBaseHandler(StaticFileHandler):
    def __init__(self, *args, **kwargs):
        super(StaticFileBaseHandler, self).__init__(*args, **kwargs)
        self.xsrf_token
