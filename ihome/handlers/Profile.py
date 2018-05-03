# coding=utf-8
import logging
import constant

from .BaseHandler import BaseHandler
from utils.commons import required_login
from utils.response_code import RET
from utils.qiniu_storage import storage


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
            img_url = constant.QINIU_URL_PREFIX + user["up_avatar"]
            pass
        else:
            img_url = None
        self.write({"errcode": RET.OK, "errmsg": "OK",
                    "data": {"user_id": user_id, "name": user["up_name"], "mobile": user["up_mobile"],
                             "avatar": img_url}})


class AvatarHandler(BaseHandler):
    """上传头像"""

    @required_login
    def post(self):
        files = self.request.files.get("avatar")
        if not files:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="未上传图片"))
        avatar = files[0]["body"]
        # 调用七牛上传图片
        try:
            file_name = storage(avatar)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.THIRDERR, errmsg="上传失败"))

        # 从session数据中取出user_id
        user_id = self.session.data["user_id"]

        # 保存图片名（即图片的url）到数据库中
        sql = "update ih_user_profile set up_avatar=%(avatar)s where up_user_id=%(user_id)s"
        try:
            row_count = self.db.execute_rowcount(sql, avatar=file_name, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="保存数据错误"))
        self.write(dict(errcode=RET.OK, errmsg="保存成功", data="%s%s" % (constant.QINIU_URL_PREFIX, file_name)))


class NameHandler(BaseHandler):
    """修改用户名"""

    @required_login
    def post(self):
        # 从session中获取用户身份信息
        user_id = self.session.data["user_id"]
        # 获取用户名
        name = self.json_args.get("name")

        # 判断是否传了name值,并且不应为空字符串
        if name in (None, ""):
            return self.write({"errcode": RET.PARAMERR, "errmsg": "params error"})
        # 保存name，并同时判断是否重复（利用数据库的唯一索引）
        try:
            self.db.execute_rowcount("update ih_user_profile set up_name=%s where up_user_id=%s", name, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "name has exist"})

        # 修改session中的name字段，并保存到redis中去
        self.session.data["name"] = name
        try:
            self.session.save()
        except Exception as e:
            logging.error(e)
        self.write({"errcode": RET.OK, "errmsg": "OK"})


class AuthHandler(BaseHandler):
    """实名认证"""
    @required_login
    def get(self):
        # 获取session中的user_id
        user_id = self.session.data["user_id"]

        # 在数据库中查询信息
        try:
            result = self.db.get("select up_real_name, up_id_card from ih_user_profile where up_user_id=%s", user_id)
        except Exception as e:
            # 数据库查询出错
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "获取数据失败"})
        logging.debug(result)
        if not result:
            return self.write({"errcode": RET.NODATA, "errmsg": "no data"})
        self.write({"errcode": RET.OK, "errmsg": "OK",
                    "data": {"real_name": result.get("up_real_name", ""), "id_card": result.get("up_id_card", "")}})

    @required_login
    def post(self):
        # 获取session中的user_id
        user_id = self.session.data["user_id"]

        # 获取传过来的数据
        real_name = self.json_args.get("real_name")
        id_card = self.json_args.get("id_card")
        if real_name in (None, "") or id_card in (None, ""):
            return self.write({"errcode": RET.PARAMERR, "errmsg": "参数错误"})
        # 校验身份证有效性（省略）
        try:
            self.db.execute_rowcount("update ih_user_profile set up_real_name=%s, up_id_card=%s where up_user_id=%s",
                                     real_name, id_card, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "update failed"})
        self.write({"errcode": RET.OK, "errmsg": "OK"})