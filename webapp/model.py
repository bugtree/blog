#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)
from orm import Model, IntField, StrField

class User(Model):
    id = IntField('id')
    usr = StrField('username')
    pwd = StrField('password')

if __name__ == '__main__':
    logging.info("attrs:%s"%User.__dict__)
    u = User(id=1024, usr='Bob', pwd='znyyddf')
    u.save()
    d = {'one':1, 'two':2}
    #logging.info(dir(d))

