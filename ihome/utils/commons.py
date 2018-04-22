# coding=utf-8
import functools

from .response_code import RET

def required_login(fun):
    # 保证被装饰函数对象的__name__属性不变
    @functools.wraps(fun)
    def wrapper(request_handler_object, *args, **kwargs):
        # 调用get_current_user方法判断用户是否登录
        if not request_handler_object.get_current_user():
            request_handler_object.write(dict(errcode=RET.SESSIONERR, errmsg="用户未登录"))
        else:
            fun(request_handler_object, *args, **kwargs)
    return wrapper