# -*- coding: UTF-8 -*-
import redis
import config
import pymysql
import hashlib
import time


class BaseApi(object):

    def __init__(self, params):
        self.uid = 0
        self.openid = ''
        self.userSessionExpire = 604800
        self.params = params
        self.config = config.get_configs()
        pool = redis.ConnectionPool(host=self.config['redis']['host'], port=self.config['redis']['port'],
                                    password=self.config['redis']['auth'], decode_responses=True)
        self.redis = redis.Redis(connection_pool=pool)
        self.db = pymysql.connect(host=self.config['mysql']['host'],
                                  port=int(self.config['mysql']['port']),
                                  user=self.config['mysql']['user'],
                                  passwd=self.config['mysql']['password'],
                                  db=self.config['mysql']['db'],
                                  charset='utf8')

    # generate user session_id
    def set_user_cookie(self):
        s = self.openid + str(time.time())
        hl = hashlib.md5()
        hl.update(s.encode(encoding='urf-8'))
        session_id = hl.hexdigest()
        self.redis.set(session_id, self.uid, self.userSessionExpire)
        return session_id

    def __del__(self):
        self.db.close()
