# coding=utf-8
import logging
import json
import constant

from .BaseHandler import BaseHandler
from utils.response_code import RET


class AreaInfoHandler(BaseHandler):
    """提供城区信息"""

    def get(self):
        # 先到redis中查询数据，如果获取到了数据，直接返回给用户
        try:
            result = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            result = None
        if result:
            # 此时从redis中读取到的数据ret是json格式字符串
            # ret = "[]"
            # 需要回传的响应数据格式json，形如：
            # '{"errcode":"0", "errmsg":"OK", "data":[]}'
            # '{"errcode":"0", "errmsg":"OK", "data":%s}' % ret
            logging.info("hit redis: area_info")
            resp = '{"errcode: "0, "errmsg": "OK", "data": %s}' % result
            return self.write(resp)

        # 查询Mysql数据库，获取城区信息
        sql = "select ai_area_id, ai_name from ih_area_info;"
        try:
            result = self.db.query(sql)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="数据库查询出错"))
        if not result:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据"))
        # 保存转换好的区域信息
        data = []
        for row in result:
            d = {
                "area_id": row.get("ai_area_id", ""),
                "name": row.get("ai_name", "")
            }
            data.append(d)
        # 在返回给用户数据之前，先向redis中保存一份数据副本
        json_data = json.dumps(data)
        try:
            self.redis.setex("area_info", constant.REDIS_AREA_INFO_EXPIRES_SECONDES, json_data)
        except Exception as e:
            logging.error(e)
        self.write(dict(errcode=RET.OK, errmsg="OK", data=data))


class IndexHandler(BaseHandler):
    """主页信息"""

    def get(self):
        try:
            result = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
            result = None
        if result:
            json_houses = result
        else:
            try:
                # 查询数据库，返回房屋订单数目最多的5条数据(房屋订单通过hi_order_count来表示）
                house_ret = self.db.query(
                    "select hi_house_id, hi_title, hi_order_count, hi_index_image_url from ih_house_info order by hi_order_count desc limit %s;" % constant.HOME_PAGE_MAX_HOUSES)
            except Exception as e:
                logging.error(e)
                return self.write({"errcode": RET.DBERR, "errmsg": "get data error"})
            if not house_ret:
                return self.write({"errcode": RET.NODATA, "errmsg": "no data"})
            houses = []
            for  l in house_ret:
                if not l["hi_index_image_url"]:
                    continue
                house = {
                    "house_id": l["hi_house_id"],
                    "title": l["hi_title"],
                    "img_url": constant.QINIU_URL_PREFIX + l["hi_index_image_url"]
                }
                houses.append(house)
                json_houses = json.dump(houses)
                try:
                    self.redis.setex("home_page_data", constant.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, json_houses)
                except Exception as e:
                    logging.error(e)

        # 返回首页城区数据
        try:
            result = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            result = None
        if result:
            json_area = result
        else:
            try:
                area_ret = self.db.query("select ai_area_id, ai_name from ih_area_info")
            except Exception as e:
                logging.error(e)
                area_ret = None
            areas = []
            if area_ret:
                for area in area_ret:
                    areas.append(dict(area_id=area["ai_area_id"], name=area["ai_name"]))
            json_areas = json.dumps(areas)
            try:
                self.redis.setex("area_info", constant.REDIS_AREA_INFO_EXPIRES_SECONDES, json_areas)
            except Exception as e:
                logging.error(e)
            resp = '{"errcode": "0", "errmsg": "OK", "houses": %s, "areas": %s}' % (json_houses, json_areas)
            self.write(resp)