# -*- coding: UTF-8 -*-
from .baseApi import BaseApi
from library.exception import *
from library.helper.myaes import MyAes
from library.helper.sts import Sts
from qcloud_cos import CosConfig, CosS3Client, CosClientError, CosServiceError
from cmq.account import Account
from cmq.cmq_exception import *
# from cmq.subscription import *
from cmq.topic import *
import requests
import logging
import json
import sys


class LifeBook(BaseApi):
    allow_visit = ("test",
                   "sign_up",
                   "get_book_info",
                   "invite_friends",
                   "commit_book_parts",
                   "get_temp_cos_keys",
                   "cmq_send_template_msg"
                   )

    def __init__(self, action, body):
        self.action = action
        self.body = body
        BaseApi.__init__(self, body)
        self.client = CosS3Client(CosConfig(Region='ap-beijing',
                                            Secret_id=self.config['cos']['secret_id'],
                                            Secret_key=self.config['cos']['secret_key']))  # 获取配置对象

    def call(self):
        if self.action in self.allow_visit:
            func = getattr(self, self.action)
            return func()
        else:
            raise ActionException("invalid action: action=%s" % self.action)

    # test
    def test(self):
        self.openid = '7898700'
        self.uid = '222'
        sid = self.set_user_cookie()
        return sid

    # 用户注册（首次或认证过期）
    def sign_up(self):
        params = self.body

        # 获取openid
        code_info = json.loads(requests.get("https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s"
                                            "&grant_type=authorization_code" % (self.config['micro_progress']['app_id'],
                                                                                self.config['micro_progress']['secret'],
                                                                                params['code'])).text)
        if 'openid' in code_info:
            self.openid = code_info['openid']
            self.cursor.execute("select id from fans where open_id = %s", self.openid)
            u_info = self.cursor.fetchone()
        else:
            raise InfoException()

        if not u_info:
            recommender_id = MyAes().decrypt(params['scene'])

            sql_insert = "INSERT INTO fans (open_id, recommender_id, avatar, nickname, gender, country, province, " \
                         "city) VALUES ('%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s')" %\
                         (self.openid, int(recommender_id), params['avatar'], params['nickname'], params['gender'],
                          params['country'], params['province'], params['city'])
            try:
                self.cursor.execute(sql_insert)
                # 提交.
                self.db.commit()
                self.uid = self.cursor.lastrowid
                sid = self.set_user_cookie()

                data = {'session_id': sid}
                return self.public_return(True, 'success', data)

            except Exception:
                # 错误回滚
                self.db.rollback()
                raise NotLoginException()
        else:
            self.uid = u_info['id']
            sid = self.set_user_cookie()

            data = {'session_id': sid}
            return self.public_return(True, 'success', data)

    # 获取纪念册信息
    def get_book_info(self):
        uid = self.get_user_session_id(self.body['session_id'])
        if not params['page'] or params['page'] < 1:
            page = 1
        else:
            page = int(params['page'])
        num_per_page = 10
        start = (page - 1) * num_per_page

        if int(self.body['unread']) == 1:
            sql = "select f.nickname as editor_nickname,f.avatar as editor_avatar,event_date,event_address," \
                  "event_description,event_images,is_read from book_parts b inner join fans f " \
                  "on b.book_owner_id=f.id where book_owner_id = %d and is_read = 0 order by event_date desc " \
                  "limit %d, %d" % (int(uid), start, num_per_page)
        else:
            sql = "select f.nickname as editor_nickname,f.avatar as editor_avatar,event_date,event_address," \
                  "event_description,event_images,is_read from book_parts b inner join fans f " \
                  "on b.book_owner_id=f.id where book_owner_id = %d order by event_date desc " \
                  "limit %d, %d" % (int(uid), start, num_per_page)

        try:
            self.cursor.execute(sql)  # 执行sql语句
            book_info = self.cursor.fetchall()  # 获取查询的所有记录
            unread_total_num = 0
            for info in range(len(book_info)):
                if book_info[info]['is_read'] == 0:
                    unread_total_num = unread_total_num + 1

            data = {
                'unread_total_num': unread_total_num,
                'parts': book_info
            }
            return self.public_return(True, 'success', data)
        except Exception:
            raise NotLoginException()

    # 邀请他人
    def invite_friends(self):
        uid = self.get_user_session_id(self.body['session_id'])

        if not uid:
            raise NotLoginException()

        scene = MyAes().encrypt(uid)
        access_token = self.search_access_token()

        if not access_token:
            access_token = self.get_access_token()
            if not access_token:
                raise AccessTokenException()

        payload = {'scene':scene}
        life_img = requests.post("https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=%s" % access_token,
                                 data=json.dumps(payload)).content
        try:
            self.client.put_object(
                Bucket=self.config['cos']['bucket'],
                Body=life_img,
                Key='wxcode/' + str(uid) + '.png',
                EnableMD5=False
            )
            qr_code_url = self.config['cos']['visit_url'] + 'wxcode/' + str(uid) + '.png'

            data = {'qr_code_url': qr_code_url}
            return self.public_return(True, 'success', data)
        except CosClientError as e:
            print(str(e))
            raise CosException()
        except CosServiceError as e:
            print(e.get_digest_msg())
            raise CosException()

    # 笔记表单提交
    def commit_book_parts(self):

        params = self.body

        uid = self.get_user_session_id(params['session_id'])
        book_owner_id = MyAes().decrypt(params['token'])

        images_str = '|'.join(self.body['event_images'])

        sql_insert = "INSERT INTO book_parts (book_owner_id, editor_id, event_date, event_address, " \
                     "event_description, event_images) VALUES ('%d', '%d', '%s', '%s', '%s', '%s')" % \
                     (int(book_owner_id), int(uid), params['event_date'], params['event_address'],
                      params['event_description'], images_str)

        try:
            self.cursor.execute(sql_insert)
            self.db.commit()
            
            # cmq todo
            endpoint = self.config['cmq']['request_url']
            try:
                my_account = Account(endpoint, self.config['cos']['secret_id'], self.config['cos']['secret_key'],
                                     debug=True)
                my_account.set_log_level(logging.DEBUG)
                topic_name = sys.argv[1] if len(sys.argv) > 1 else "lifebook"
                my_topic = my_account.get_topic(topic_name)

                self.cursor.execute("select id,open_id,nickname from fans where id = %s", int(book_owner_id))
                u_info = self.cursor.fetchone()

                message_body = {
                    "openid": u_info['open_id'],
                    "nickname": u_info['nickname'],
                    "created_at": params['event_date']
                }
                message = Message()
                message.msgBody = json.dumps(message_body)
                my_topic.publish_message(message)
            except CMQExceptionBase as e:
                print("cmqException:%s\n" % e)

            return self.public_return(True, 'success', {})

        except Exception:
            # self.db.rollback()
            raise InfoException()

    # 获取cos图片上传临时凭证
    def get_temp_cos_keys(self):
        uid = self.get_user_session_id(self.body['session_id'])
        config = {
            # 临时密钥有效时长，单位是秒
            'duration_seconds': 1800,
            # 固定密钥
            'secret_id': self.config['cos']['secret_id'],
            # 固定密钥
            'secret_key': self.config['cos']['secret_key'],
            'proxy': '',
            # 换成你的 bucket
            'bucket': self.config['cos']['bucket'],
            # 换成 bucket 所在地区
            'region': 'ap-beijing',
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的目录，例子：* 或者 a/* 或者 a.jpg
            'allow_prefix': 'book_imgs/*',
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看
            'allow_actions': [
                'name/cos:PutObject'
            ]

        }

        sts = Sts(config)
        response = sts.get_credential()

        data = {
            "credentials": {
                "tmp_secret_id": response['credentials']['tmpSecretId'],
                "tmp_secret_key": response['credentials']['tmpSecretKey'],
                "session_token": response['credentials']['sessionToken']
            },
            "expired_time": response['expiredTime']
        }
        return self.public_return(True, 'success', data)

    # 消息推送
    def cmq_send_template_msg(self):

        access_token = self.search_access_token()
        if not access_token:
            access_token = self.get_access_token()
            if not access_token:
                raise AccessTokenException()

        payload = {
            'touser': self.body['openid'],
            'template_id': 'SbQB8QyBvfVOyco10zgkhUqcCLoAW8zX0fest99VI5A',
            'form_id': 'FORMID',
            'data':{
                'keyword1': {'value': '信息内容'},
                'keyword2': {'value': '2222222'},
                'keyword3': {'value': self.body['created_at']},
                'keyword4': {'value': self.body['nickname']}
            }
        }
        response = requests.post("https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=%s" %
                                 access_token, data=json.dumps(payload)).content

        return response





