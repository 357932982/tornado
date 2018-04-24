# coding=utf-8
import os

from handlers import Passport, VerifyCode, Profile
from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler

handlers = [

    (r"/api/piccode", VerifyCode.PicCodeHandler),
    (r"/api/smscode", VerifyCode.SMSCodeHandler),
    (r"/api/register", Passport.RegisterHandler),
    (r"/api/login", Passport.LoginHandler),
    (r"/api/logout", Passport.LogoutHandler),
    (r"/api/check_login", Passport.CheckLoginHandler),
    (r"/api/profile", Profile.ProfileHandler),
    (r"/(.*)", StaticFileHandler,
     dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html")),
]
