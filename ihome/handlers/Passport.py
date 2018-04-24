# coding=utf-8
import logging
import hashlib

import config

from utils.session import Session
from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.commons import required_login


class RegisterHandler(BaseHandler):
    def post(self):
        mobile = self.json_args.get("mobile")
        sms_code = self.json_args.get("phonecode")
        password = self.json_args.get("password")

        """验证短信验证码"""
        try:
            real_sms_code = self.redis.get("sms_code_%s" % mobile)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询验证码出错"))
        if not real_sms_code:
            return self.write(dict(errcode=RET.NODATA, errmsg="验证码过期"))

        # 对比短信验证码
        if real_sms_code != sms_code:
            return self.write(dict(errcode=RET.DATAERR, errmsg="验证码错误"))
        # 删除redis中的验证码
        try:
            self.redis.delete("sms_code_%s" % sms_code)
        except Exception as e:
            logging.error(e)

        """保存注册信息,同时根据mobile字段唯一性判断手机号码是否已注册"""
        passwd = hashlib.sha256(password + config.passwd_hash_key).hexdigest()
        sql = "insert into ih_user_profile(up_name, up_mobile, up_passwd) values (%(name)s, %(mobile)s, %(passwd)s )"
        try:
            user_id = self.db.execute(sql, name=mobile, mobile=mobile, passwd=passwd)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DATAEXIST, errmsg="该手机号码已注册"))
        

        # 将登录状态记录到session
        session = Session(self)
        session.data["user_id"] = user_id
        session.data["mobile"] = mobile
        session.data["name"] = mobile
        try:
            session.save()
        except Exception as e:
            logging.error(e)
        self.write(dict(errcode=RET.OK, errmsg="注册成功"))


class LoginHandler(BaseHandler):
    def post(self):
        mobile = self.json_args.get("mobile")
        password = self.json_args.get("password")
        # 参数检验
        if not all([mobile, password]):
            return self.write(dict(errcode=RET.PARAMERR, errmsg="参数错误"))
        # 对取到的密码进行加密，然后与数据库中存的密码进行比对
        passwd = hashlib.sha256(password + config.passwd_hash_key).hexdigest()
        sql = "select up_user_id, up_name, up_mobile, up_passwd from ih_user_profile where up_mobile = %(mobile)s"
        try:
            user = self.db.get(sql, mobile=mobile)
        except Exception as e:
            logging.error(e)
        if user and user["up_passwd"] == unicode(passwd):
            # 生成session数据，并且返回给客户端信息
            session = Session(self)
            session.data["user_id"] = user["up_user_id"]
            session.data["name"] = user["up_name"]
            session.data["mobile"] = user["up_mobile"]
            try:
                session.save()
            except Exception as e:
                logging.error(e)
            self.write(dict(errcode=RET.OK, errmsg="OK"))
        else:
            self.write(dict(errcode=RET.DATAERR, errmsg="帐号或密码错误"))


class LogoutHandler(BaseHandler):
    """退出登录"""
    @required_login
    def get(self):
        # 清除session数据
        session = Session(self)
        session.clear()
        self.write(dict(errcode=RET.OK, errmsg="退出登录成功"))


class CheckLoginHandler(BaseHandler):
    """检查登录状态"""
    def get(self):
        if self.get_current_user():
            self.write({"errcode": RET.OK, "errmsg": "true", "data": {"name": self.session.data.get("name")}})
            print self.session.data
        else:
            self.write({"errcode": RET.SESSIONERR, "errmsg": "false"})

