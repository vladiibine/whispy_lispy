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

    def __hash__(self):
        return hash(self.values)


class String(Type):
    @classmethod
    def from_quoted_values(cls, values):
        """The concrete syntax nodes didn't know much difference
        between strings and symbols. They determined the difference between
        these by letting the start and end quotes on the strings.

        This "madness" stops here"""

        return cls((values[0][1:-1],))

    def __repr__(self):
        return '$String {}'.format(self.values[0])

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.values == other.values


class Int(Type):
    def __repr__(self):
        return '$Int {}'.format(self.values[0])


class Bool(Type):
    def __repr__(self):
        return '$Bool {}'.format(self.values[0])


class Float(Type):
    def __repr__(self):
        return '$Float {}'.format(self.values[0])


class List(Type):
    def __repr__(self):
        return '$List {}'.format(self.values)


class Symbol(Type):
    def __repr__(self):
        return '$Symbol {}'.format((self.values[0]))


class Function(Type):
    """The Function object.

    Its values list must contain (on the given positions):
    0: the function name
    1: the function argument names
    2: the AST that will get executed

    ...Stuff will get added here (like the closure scope)
    """
    def __repr__(self):
        return '$[Func {name} at {address}]'.format(
            name=self.values[0], address=id(self))
