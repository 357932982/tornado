# coding=utf-8

import json

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
        """预处理json"""
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = {}

    def write_error(self, status_code, **kwargs):
        pass

    def set_default_headers(self):
        """设置默认json格式"""
        self.set_header("Content_Type", "application/json; charset=utf-8")

    def initialize(self):
        pass

    def on_finish(self):
        pass


class StaticFileBaseHandler(StaticFileHandler):
    def __init__(self, *args, **kwargs):
        super(StaticFileBaseHandler, self).__init__(*args, **kwargs)
        self.xsrf_token
