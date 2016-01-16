from core.Cipher import DES
from hashlib import md5
import hashlib
import base64
import re
import os

'''
PBEWithMD5AndDES port based on

'''
class PBEWithMD5AndDES():

    @staticmethod
    def get_derived_key(password, salt, count):
        key = password + salt
        for i in range(count):
            m = hashlib.md5(key)
            key = m.digest()
        return (key[:8], key[8:])

    @staticmethod
    def decrypt(msg, password):
        msg_bytes = base64.b64decode(msg)
        salt = msg_bytes[:8]
        enc_text = msg_bytes[8:]
        (dk, iv) = PBEWithMD5AndDES.get_derived_key(password, salt, 1000)
        crypter = DES.new(dk, DES.MODE_CBC, iv)
        text = crypter.decrypt(enc_text)
        # remove the padding at the end, if any
        return re.sub(r'[\x01-\x08]','',text)

    @staticmethod
    def encrypt(msg, password):
        salt = os.urandom(8)
        pad_num = 8 - (len(msg) % 8)
        for i in range(pad_num):
            msg += chr(pad_num)
        (dk, iv) = PBEWithMD5AndDES.get_derived_key(password, salt, 1000)
        crypter = DES.new(dk, DES.MODE_CBC, iv)
        enc_text = crypter.encrypt(msg)
        return base64.b64encode(salt + enc_text)