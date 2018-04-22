# coding=utf-8
import random
import re
import logging
from constant import PIC_CODE_EXPIRES_SECONDS, SMS_CODE_EXPIRES_SECONDS
from BaseHandler import BaseHandler
from utils.captcha.captcha import captcha
from utils.response_code import RET
from libs.yuntongxun.SendTemplateSMS import ccp


class PicCodeHandler(BaseHandler):
    """图片验证码"""
    def get(self):
        """获取图片验证码"""
        code_id = self.get_argument("codeid")
        pre_code_id = self.get_argument("pre_code_id")
        if pre_code_id:
            try:
                self.redis.delete("pic_code_%s" % pre_code_id)
            except Exception as e:
                logging.error(e)
        # name 图片验证码名称
        # text 图片验证码文本
        # image 图片验证码二进制数据
        name, text, image = captcha.generate_captcha()
        try:
            self.redis.setex("pic_code_%s" % code_id,
                             PIC_CODE_EXPIRES_SECONDS, text)
        except Exception as e:
            logging.error(e)
            self.write("")
        self.set_header("Content-Type", "image/jpg")
        self.write(image)


class SMSCodeHandler(BaseHandler):
    """短信验证码"""
    def post(self):
        """获取参数"""
        mobile = self.json_args.get("mobile")
        piccode = self.json_args.get("piccode")
        piccode_id =self.json_args.get("piccode_id")
        print "*"*30
        print mobile
        print piccode
        print piccode_id
        print "*"*30

        """获取图片验证码真是值"""
        try:
            real_piccode = self.redis.get("pic_code_%s" % piccode_id)
            print real_piccode
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询验证码错误"))
        if not real_piccode:
            return self.write(dict(errcode=RET.NODATA, errmsg="验证码过期"))

        """删除图片验证码"""
        try:
            self.redis.delete("pic_code_%s" % piccode_id)
        except Exception as e:
            logging.error(e)

        if real_piccode.lower() != piccode.lower():
            return self.write(dict(errcode=RET.DATAERR, errmsg="验证码错误"))

        # 验证手机号码是否存在
        sql = "select count(*) counts from ih_user_profile where up_mobile = %s"
        try:
            ret = self.db.get(sql, mobile)
        except Exception as e:
            logging.error(e)
        else:
            if 0 != ret["counts"]:
                return self.write(dict(errcode=RET.DATAEXIST, errmsg="该手机号已注册"))

        # 产生随机验证码
        sms_code = "%06d" % random.randint(0, 1000000)
        try:
            self.redis.setex("sms_code_%s" % mobile, SMS_CODE_EXPIRES_SECONDS, sms_code)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="数据库出错"))


         # 发送短信验证码
        try:
            result = ccp.sendTemplateSMS(mobile, [sms_code, SMS_CODE_EXPIRES_SECONDS], 1)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.THIRDERR, errmsg="发送短信失败"))
        if result:
            self.write(dict(errcode=RET.OK, errmsg="发送成功"))
        else:
            self.write(dict(errcode=RET.UNKOWNERR, errmsg="发送失败"))