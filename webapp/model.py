#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

import time, uuid
from orm import Model, StringField, BooleanField, InterField, FloatField, TextField 

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

#此处变量名称应该与数据库表中的字段名称完全对应

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='vchar(50)')
    name = StringField(ddl='vchar(50)')
    password = StringField(ddl='vchar(50)')
    email = StringField(ddl='vchar(50)')
    admin = BooleanField()
    image = StringField(ddl='vchar(500)')
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    view_count = InterField()
    created_at = FloatField(default=time.time)
    cat_id = StringField(ddl='varchar(50)')
    cat_name = StringField(ddl='varchar(50)')

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Category(Model):
    __table__ = 'categorys'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    created_at = FloatField(default=time.time)
