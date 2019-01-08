# -*- coding: UTF-8 -*-
import json
import traceback
from library.lifeBook import LifeBook
from library.exception import *


def main_handler(event, context):
    print('ready ! go !')

    if 'Records' in event and 'CMQ' in event['Records'][0]:
        action = "cmq_send_template_msg"
        body = json.loads(event['Records'][0]['CMQ']['msgBody'])

    else:
        action = event['pathParameters']['action']
        body = json.loads(event['body'])

    try:
        life_book = LifeBook(action, body)
        return life_book.call()
    except ActionException as e:
        return {
            'ret': False,
            'code': 'actionError',
            'message': str(e),
            'data': {}
        }
    except NotLoginException:
        return {
            'ret': False,
            'code': 'NotLogin',
            'message': '',
            'data': {}
        }
    except InfoException as e:
        return {
            'ret': False,
            'code': 'InfoError',
            'message': str(e),
            'data': {}
        }
    except AccessTokenException:
        return {
            'ret': False,
            'code': 'AccessTokenError',
            'message': '',
            'data': {}
        }
    except Exception:
        print(traceback.format_exc())
        return {
            'ret': False,
            'code': 'otherError',
            'message': traceback.format_exc(),
            'data': {}
        }

# just for test
# event1 = {
#     'pathParameters': {
#         'action': 'sign_up'
#     },
#     'body': json.dumps({
#         'code':'001pTBDP14M9P11PY3EP1F4ODP1pTBDw',
#         'nickname':'aaa',
#         'avatar':'touxiang',
#         'gender':'1',
#         'country':'chain',
#         'province':'北京',
#         'city':'北京市',
#         'scene':'69dc43b5135f7c1ee0edba6f4f48b809',
#         'session_id':'7d2912521e4e576c20413611adabdcbb'
#         # 'session_id':'c92d9b2286926fa6ebcd7ca7056692b1'
#         # 'session_id':'d0f93b9a7536edc7a9a12e3d98a4ccc0'
#     }),
#     'headers': {}
# }

# 获取纪念册信息
# event1 = {
#     'pathParameters': {
#         'action': 'get_book_info'
#     },
#     'body': json.dumps({
#         'session_id':'7d2912521e4e576c20413611adabdcbb',
#         'unread': '0'
#     }),
#     'headers': {}
# }

# 邀请他人
# event1 = {
#     'pathParameters': {
#         'action': 'invite_friends'
#     },
#     'body': json.dumps({
#         'session_id':'7d2912521e4e576c20413611adabdcbb'
#     }),
#     'headers': {}
# }


event1 = {
    'pathParameters': {
        'action': 'test'
    },
    'body': json.dumps({
        'session_id':'773629da474335513b83971aee680e5b'
    }),
    'headers': {}
}


# 笔记表单提交
# event1 = {
#     'pathParameters': {
#         'action': 'commit_book_parts'
#     },
#     'body': json.dumps({
#         'session_id':'fac7f578b4fd1920e7c7035354ecae9d',
#         'token':'69dc43b5135f7c1ee0edba6f4f48b809',
#         'event_date':'2018-06-06',
#         'event_description':'1',
#         'event_images':['imageone']
#     }),
#     'headers': {}
# }


# 获取纪念册信息
# event1 = {
#     'pathParameters': {
#         'action': 'get_temp_cos_keys'
#     },
#     'body': json.dumps({
#         'session_id':'7d2912521e4e576c20413611adabdcbb'
#     }),
#     'headers': {}
# }

# 消息推送
# event1 = {
#     "Records": [
#         {
#           "CMQ": {
#             "msgBody": "{\"openid\":\"okqgc5GzfcO-B2oOk9Ew0PTBWyOg\",\"nickname\":\"lewe\",\"created_at\":\"2018-08-12\"}",
#             "msgId": "8725724278030337",
#             "msgTag": "",
#             "publishTime": "2018-12-22T14:46:49Z",
#             "requestId": "2207663515579660723",
#             "subscriptionName": "lifebook",
#             "topicName": "lifebook",
#             "topicOwner": 1253333841,
#             "type": "topic"
#           }
#         }
#     ]
# }
context1 = {}
print(main_handler(event1, context1))

