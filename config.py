# -*- coding: utf8 -*-


def get_configs(environment='development'):
    configs = {
        'development': {
            'mysql': {
                'host': '127.0.0.1',
                'port': 3306,
                'user': '',
                'password': '',
                'db': ''
            },
            'redis': {
                'host': '127.0.0.1',
                'port': 6379,
                'auth': ''
            },
            'aes': {
                'key': ''
            },
            'cos': {
                'bucket': 'lifebook-1253333841',
                'visit_url': 'https://lifebook-1253333841.cos.ap-beijing.myqcloud.com/',
                'secret_id': '',
                'secret_key': ''
            },
            'micro_progress': {
                'app_id': '',
                'secret': ''
            },
            'cmq': {
                'request_url': 'https://cmq-topic-bj.api.qcloud.com'
            }
        },
        'production': {
            'mysql': {
                'host': '127.0.0.1',
                'port': 3306,
                'user': '',
                'password': '',
                'db': ''
            },
            'redis': {
                'host': '127.0.0.1',
                'port': 6379,
                'auth': ''
            },
            'aes': {
                'key': ''
            },
            'cos': {
                'bucket': '',
                'visit_url': '',
                'secret_id': '',
                'secret_key': ''
            },
            'micro_progress': {
                'app_id': '',
                'secret': ''
            },
            'cmq': {
                'request_url': 'http://cmq-topic-bj.api.tencentyun.com'
            }
        }

    }
    return configs[environment]
