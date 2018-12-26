# -*- coding: UTF-8 -*-
import json
import config
import pymysql
import hashlib
import time
import requests
from library.helper.myredis import MyRedis


class BaseApi(object):

    def __init__(self, params):
        self.uid = ''
        self.openid = ''
        self.userSessionExpire = 604800
        self.params = params
        self.config = config.get_configs()
        self.accessTokenExpire = 6000
        self.db = pymysql.connect(host=self.config['mysql']['host'],
                                  port=int(self.config['mysql']['port']),
                                  user=self.config['mysql']['user'],
                                  passwd=self.config['mysql']['password'],
                                  db=self.config['mysql']['db'],
                                  charset='utf8')
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        self.redis = MyRedis(self.config['redis'])

    # generate user session_id
    def set_user_cookie(self):
        s = self.openid + str(time.time())
        hl = hashlib.md5()
        hl.update(s.encode(encoding='utf-8'))
        session_id = hl.hexdigest()
        self.redis.set(session_id, self.uid, self.userSessionExpire)
        return session_id

    def get_user_session_id(self, session_id):
        return self.redis.get(session_id)

    # 获取Access_Token
    def get_access_token(self):
        geturl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" %\
                 (self.config['mycro_progress']['appid'], self.config['micro_progress']['secret'])
        ret = requests.get(geturl).text
        ret_arr = json.loads(ret)

        if 'access_token' in ret_arr:
            self.redis.set('access_token', ret_arr['access_token'], self.accessTokenExpire)
            return ret_arr['access_token']

    # 从redis中获取Access_Token
    def search_access_token(self):
        return self.redis.get('access_token')

    def public_return(self, ret, message, data):
        return {
            'ret': ret,
            'message': message,
            'data': data
        }

    def __del__(self):
        self.db.close()
