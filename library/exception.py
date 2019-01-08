# -*- coding: utf-8 -*-


class ExceptionBase(Exception):

    def __init__(self, message):
        self.message = message

    def get_info(self):
        return 'Error Message: %s \n' % self.message

    def __str__(self):
        return 'ApiException  %s' % (self.get_info())


class ActionException(ExceptionBase):

    def __init__(self, message):
        ExceptionBase.__init__(self, message)

    def __str__(self):
        return 'ActionException: %s' % (self.get_info())


class NotLoginException(Exception):
    pass


class NetworkException(Exception):
    pass


# Cos上传异常
class CosException(Exception):
    pass


# 获取AccessToken异常
class AccessTokenException(Exception):
    pass


class InfoException(ExceptionBase):

    def __init__(self, message):
        ExceptionBase.__init__(self, message)

    def __str__(self):
        return 'InfoException: %s' % (self.get_info())
