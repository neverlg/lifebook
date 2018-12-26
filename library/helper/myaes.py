# -*- coding: UTF-8 -*-
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import config


class MyAes(object):

    def __init__(self):
        self.config = config.get_configs()
        self.key = self.config['aes']['key']
        self.mode = AES.MODE_CBC

    # AES加密
    def encrypt(self, text):
        crypt = AES.new(self.key, self.mode, self.key)

        length = 16
        count = len(text)

        if count % length != 0:
            add = length - (count % length)
        else:
            add = 0

        text = text + ('\0' * add)
        cipher_text = crypt.encrypt(text)

        return b2a_hex(cipher_text).decode()

    # AES解密
    def decrypt(self, text):
        crypt = AES.new(self.key, self.mode, self.key)
        plain_text = crypt.decrypt(a2b_hex(text))
        return plain_text.decode().rstrip('\0')
