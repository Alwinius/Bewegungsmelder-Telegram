#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)


from sqlalchemy import TypeDecorator, cast, String
from bot.components.category import Category

import json


class ArrayOfEnum(TypeDecorator):
    """ Sqlite-like does not support arrays.
        Let's use a custom type decorator.

        See http://docs.sqlalchemy.org/en/latest/core/types.html#sqlalchemy.types.TypeDecorator
    """
    impl = String

    def process_bind_param(self, value, dialect):
        string_list = []
        for v in value:
            string_list.append(v.name)
        return json.dumps(string_list)

    def process_result_value(self, value, dialect):
        ret = json.loads(value)
        cat_list = []
        for r in ret:
            cat_list.append(Category[r])
        return cat_list

    def copy(self):
        return ArrayOfEnum(self.impl.length)
