# -*- coding: UTF-8 -*-
import redis


class MyRedis(object):

    def __init__(self, config):
        self.prefix_key = 'life_book_'
        pool = redis.ConnectionPool(host=config['host'], port=config['port'],
                                    password=config['auth'], decode_responses=True)
        self.redis = redis.Redis(connection_pool=pool)

    # set redis
    def set(self, key, val, expire):
        key = self.prefix_key + key
        return self.redis.set(key, val, expire)

    # set redis
    def get(self, key):
        key = self.prefix_key + key
        return self.redis.get(key)


