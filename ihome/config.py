# coding=utf-8
import os

# Application配置参数
settings = dict(
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "template"),
    cookie_secret='3AmqFZH+Q222ZNCsl4L7qXefd0QzFEdPkqD8ek/9zww=',
    xsrf_cookies=True,
    debug=True,
)

# mysql
mysql_options = dict(
    host="127.0.0.1",
    database="ihome",
    user="root",
    password="root"
)

# redis
redis_options = dict(
    host="127.0.0.1",
    port="6379"
)

# 日志配置
log_path = os.path.join(os.path.join(os.path.dirname(__file__), "logs/log"))
log_level = "debug"
