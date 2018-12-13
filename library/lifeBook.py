# -*- coding: UTF-8 -*-
from .baseApi import BaseApi
from library.exception import ActionException


class LifeBook(BaseApi):

    def __init__(self, action, body):
        self.action = action
        BaseApi.__init__(self, body)

    def call(self):
        methods = dir(self)
        if self.action in methods:
            func = getattr(self, self.action)
            return func()
        else:
            raise ActionException("invalid action: action=%s" % self.action)

    # test
    def test(self):
        return 666




