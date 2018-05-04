# -*- coding: utf-8 -*-

import qiniu.config
import logging

from qiniu import Auth, put_data, etag, urlsafe_base64_encode, put_file

# 需要填写你的 Access Key 和 Secret Key
access_key = 'lSqQ5IdOY22n7y4OqlVEv-LYJ7_VNqQHlczoxeY3'
secret_key = 'BdLVl1zLytC8vHgo48SmP2NtwbIlJq1W3-v26P9F'


def storage(file_data):
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 要上传的空间
        bucket_name = 'ihome'

        # 上传到七牛后保存的文件名
        # key = 'my-python-logo.png';

        # 生成上传 Token，可以指定过期时间等

        token = q.upload_token(bucket_name)

        # 要上传文件的本地路径
        # localfile = '/home/sony/Desktop/abc.JPG'
        # ret, info = put_file(token, None, localfile)
        ret, info = put_data(token, None, file_data)
    except Exception as e:
        logging.error(e)
        raise e
    print(ret)
    print("*" * 16)
    print(info)
    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)
    print(type(info))
    print(info.status_code)
    if 200 == info.status_code:
        return ret["key"]
    else:
        raise Exception("上传失败")


if __name__ == "__main__":
    file_name = 'test1.jpg'
    with open(file_name, "rb") as file:
        file_data = file.read()
        storage(file_data)
