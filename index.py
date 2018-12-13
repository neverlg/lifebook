# -*- coding: UTF-8 -*-
import json
import traceback
from library.lifeBook import LifeBook
from library.exception import ActionException


def main_handler(event, context):
    print('ready ! go !')

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
    except Exception:
        print(traceback.format_exc())
        return {
            'ret': False,
            'code': 'otherError',
            'message': traceback.format_exc(),
            'data': {}
        }

# just for test
event1 = {
    'pathParameters': {
        'action': 'test'
    },
    'body': json.dumps({
        'nickname': 'sss'
    }),
    'headers': {}
}
context1 = {}
print(main_handler(event1, context1))

