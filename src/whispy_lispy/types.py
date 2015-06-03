# -*- coding utf-8 -*-
"""Define the base whispy lispy types

From now on, all the functions will operate on these
"""
from __future__ import unicode_literals, absolute_import


class Type(object):
    """Abstract base type"""
    def __init__(self, values):
        """
        :param tuple values: a tuple of values
        """
        self.values = values

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.values == other.values

class String(Type):
    pass


class Int(Type):
    def __repr__(self):
        return '{Int {} }'.format(self.values[0])


class Bool(Type):
    pass


class Float(Type):
    pass


class List(Type):
    def __repr__(self):
        return '$List {}'.format(self.values)
    pass


class Symbol(Type):
    def __repr__(self):
        return '$Symbol {}'.format((self.values[0]))
