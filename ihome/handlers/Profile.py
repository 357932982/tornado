# coding=utf-8
import logging

from .BaseHandler import BaseHandler
from utils.commons import required_login
from utils.response_code import RET


class ProfileHandler(BaseHandler):
    """个人信息"""
    @required_login
    def get(self):
        user_id = self.session.data["user_id"]
        sql = "select up_name, up_mobile, up_avatar from ih_user_profile where up_user_id=%s"
        try:
            user = self.db.get(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "查询数据库错误"})
        if user["up_avatar"]:
            # img_url = constants.QINIU_URL_PREFIX + user["up_avatar"]
            pass
        else:
            img_url = None
        self.write({"errcode": RET.OK, "errmsg": "OK",
                   "data": {"user_id": user_id, "name": user["up_name"], "mobile": user["up_mobile"], "avatar": img_url}})