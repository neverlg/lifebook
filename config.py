# -*- coding: utf8 -*-


def get_configs(environment='development'):
    configs = {
        'development': {
            'mysql': {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': '123456',
                'db': 'lifebook'
            },
            'redis': {
                'host': '127.0.0.1',
                'port': 6379,
                'auth': ''
            }
        },
        'production': {
            'mysql': {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': '123456'
            },
            'redis': {
                'host': '127.0.0.1',
                'port': 6379,
                'auth': ''
            }
        }

    }
    return configs[environment]
