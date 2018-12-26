# -*- coding:utf-8 -*-
import hashlib
import hmac
import time
import urllib
import json
import requests
import random
import base64
from functools import reduce


class Sts:

    def __init__(self, config):

        if 'allow_actions' in config:
            self.allow_actions = config['allow_actions']
        else:
            raise ValueError('missing allow_actions')

        if config['duration_seconds']:
            self.duration = config['duration_seconds']
        else:
            self.duration = 1800

        self.sts_domain = 'sts.api.qcloud.com'
        self.sts_url = 'sts.api.qcloud.com/v2/index.php'
        self.sts_scheme = 'https://'

        self.secret_id = config['secret_id']
        self.secret_key = config['secret_key']
        self.proxy = config['proxy']
        self.region = config['region']

        bucket = config['bucket']
        split_index = bucket.rfind('-')
        short_bucket_name = bucket[:split_index]
        appid = bucket[(split_index+1):]

        self.resource = "qcs::cos:{region}:uid/{appid}:prefix//{appid}/{short_bucket_name}/{allow_prefix}".format(
            region=config['region'], appid=appid, short_bucket_name=short_bucket_name,
            allow_prefix=config['allow_prefix']
        )

    def get_credential(self):
        try:
            import ssl
        except ImportError as e:
            raise e

        policy = {
            'version': '2.0',
            'statement': {
                'action': self.allow_actions,
                'effect': 'allow',
                'principal': {'qcs': '*'},
                'resource': self.resource
            }
        }
        policy_encode = urllib.parse.quote(json.dumps(policy))

        data = {
            'Region':self.region,
            'SecretId':self.secret_id,
            'Timestamp':int(time.time()),
            'Nonce':random.randint(100000, 200000),
            'Action':'GetFederationToken',
            'durationSeconds':self.duration,
            'name':'cos-sts-python',
            'policy':policy_encode
        }
        data['Signature'] = self.__encrypt('POST', self.sts_url, data)

        try:
            response = requests.post(self.sts_scheme + self.sts_url, proxies=self.proxy, data=data)
            result_json = response.json()

            if isinstance(result_json['data'], dict):
                result_json = result_json['data']          
            result_json['startTime'] = int(time.time())
            
            return result_json
        except urllib.error.HTTPError as e:
            raise e

    def __encrypt(self, method, url, key_values):
        source = Tools.flat_params(key_values)
        source = method + url + '?' + source
        # sign = hmac.new(self.secret_key, source, hashlib.sha1).digest().encode('base64').rstrip()
        sign_str = hmac.new(bytes(self.secret_key,'utf-8'), bytes(source,'utf-8'), hashlib.sha1).digest()
        sign = base64.b64encode(sign_str).rstrip()
        return sign.decode()


class Tools(object):

    @staticmethod
    def _flat_key_values(a):
        return a[0] + '=' + str(a[1])

    @staticmethod
    def _link_key_values(a, b):
        return a + '&' + b

    @staticmethod
    def flat_params(key_values):
        key_values = sorted(key_values.items(), key=lambda d: d[0])
        return reduce(Tools._link_key_values, map(Tools._flat_key_values, key_values))
