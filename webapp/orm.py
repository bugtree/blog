#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

class Field(object):
    def __init__(self, name, type):
        logging.info("Field: name:%s, type:%s" % (name, type))
        self.name = name
        self.type = type

class IntField(Field):
    def __init__(self, name):
        super(IntField, self).__init__(name, 'bigint')

class StrField(Field):
    def __init__(self, name):
        super(StrField, self).__init__(name, 'vchar(100)')

# 1. 添加__table__属性，保存表名
# 2. 在当前类（比如User）中查找定义的类的所有属性，如果找到一个Field属性，就把它保存到一个__mappings__的dict中，同时从类属性中删除该Field属性，否则，容易造成运行时错误（实例的属性会遮盖类的同名属性）；
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        logging.info("ModelMetaclass: name:%s" % name)
        logging.info("ModelMetaclass: base:%s" % bases)
        logging.info("ModelMetaclass: attr:%s" % attrs)
        if name == 'Model':
            return super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)
        logging.info('find model:%s' % name)

        mappings = dict()

        for k, v in attrs.items():
            if (isinstance(v, Field)):
                mappings[k] = v
                #attrs.pop(k)
        #将此操作从上面语句中拿出，是为了规避Error: RuntimeError, items size changed
        for k in mappings:
            attrs.pop(k)
        attrs['__mappings__'] = mappings
        attrs['__table__'] = name
        
        return super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    # getattr与setattr是dict的方法，需要overwrite，以便完成Model类字典的赋值与获取字典值
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
    def __setattr__(self, key, value):
        self[key] = value

    def save(self):
        fields = []
        params = []
        args = []

        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))

        sql = 'insert into %s (%s) values (%s)'% (self.__table__, ','.join(fields), ','.join(params))
        logging.info("sql: %s" %sql)
        logging.info('args: %s' %str(args))


