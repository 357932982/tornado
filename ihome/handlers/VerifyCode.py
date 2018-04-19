# coding=utf-8
import logging
from constant import PIC_CODE_EXPIRES_SECONDS
from BaseHandler import BaseHandler
from utils.captcha.captcha import captcha


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

