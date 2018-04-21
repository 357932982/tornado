# coding=utf-8
import logging
from utils.session import Session

from .BaseHandler import BaseHandler
from utils.response_code import RET


class RegisterHandler(BaseHandler):
    def post(self):
        mobile = self.json_args.get("mobile")
        sms_code = self.json_args.get("phoneCode")
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
        sql = "insert into ih_user_profile(up_name, up_mobile, up_passwd) values (%(name)s, %(mobile)s, %(passwd)s )"
        try:
            user_id = self.db.execute(sql, name=mobile, mobile=mobile, passwd=password)
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