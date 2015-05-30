# -*- coding utf-8 -*-
"""Abstract syntax tree stuff
"""
from __future__ import unicode_literals
import six

from whispy_lispy import exceptions


DEFINITION = 'def'
QUOTE = "'"
EVAL = "eval"


class AbstractSyntaxNode(object):
    """An abstract syntax node"""
    __slots__ = ['values']

    def __init__(self, values):
        """
        :type values: tuple
        """
        self.values = values

    def __eq__(self, other):
        if other is None:
            return False
        if self.__class__ != other.__class__:
            return False
        return self.values == other.values

    def __getitem__(self, item):
        return self.values[item]

    def __repr__(self):
        return '<aN {}>'.format(self.values)

    def is_root(self):
        return isinstance(self, RootAbstractSyntaxNode)

    def is_leaf(self):
        return all(
            not isinstance(elem, AbstractSyntaxNode) for elem in self.values)

    def alike(self, values):
        """Create a new node, with the same type as the current one"""
        return self.__class__(values)


class RootAbstractSyntaxNode(AbstractSyntaxNode):
    """The abstract node marking the root of the node hierarchy"""
    def __repr__(self):
        return '<RaN {}>'.format(self.values)


class Apply(AbstractSyntaxNode):
    """Abstract apply"""
    __slots__ = ['values']

    def __repr__(self):
        return '<Apply {}>'.format(self.values)


class Quote(AbstractSyntaxNode):
    """Abstract quote"""
    __slots__ = ['values']

    def __repr__(self):
        return '<Quote {}>'.format(self.values)


class OperatorQuote(AbstractSyntaxNode):
    """Represents the quote operator ' """
    __slots__ = ['values']

    def __repr__(self):
        return '<QuoteOP>'


class Symbol(AbstractSyntaxNode):
    """Represents a symbol (variable or function name)"""
    __slots__ = ['values']

    def __repr__(self):
        return '<Symb: {}>'.format(self.values[0])


class Int(AbstractSyntaxNode):
    """Represents an integer value"""
    __slots__ = ['values']

    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Float(AbstractSyntaxNode):
    """Represents a floating point value"""
    __slots__ = ['values']

    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Bool(AbstractSyntaxNode):
    """Represents a boolean value"""
    __slots__ = ['values']

    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Assign(AbstractSyntaxNode):
    """Represent the assignment of a value to a symbol

    Will be evaluated in a certain scope
    """
    __slots__ = ['values']

    def __repr__(self):
        if len(self.values) != 2:
            return '<Invalid Assign>'
        return '<Assign {} := {} >'.format(self.values[0], self.values[1])
