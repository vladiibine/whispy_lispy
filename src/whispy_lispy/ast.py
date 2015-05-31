# -*- coding utf-8 -*-
"""Abstract syntax tree stuff
"""
from __future__ import unicode_literals
from whispy_lispy import syntax

class AbstractSyntaxNode(object):
    """An abstract syntax node"""
    def __init__(self, values, evaluable=True):
        """
        :type values: tuple
        """
        self.values = values
        self.evaluable = evaluable

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

    def is_evaluable(self):
        """Whether this should be 'instantly' evaluated or is quoted"""
        return self.evaluable

    def alike(self, values, evaluable=True):
        """Create a new node, with the same type as the current one"""
        return self.__class__(values, evaluable)


class RootAbstractSyntaxNode(AbstractSyntaxNode):
    """The abstract node marking the root of the node hierarchy"""
    def __repr__(self):
        return '<RaN {}>'.format(self.values)


class Apply(AbstractSyntaxNode):
    """Abstract apply"""
    def __repr__(self):
        return '<Apply {}>'.format(self.values)


class Quote(AbstractSyntaxNode):
    """Abstract quote"""
    def __repr__(self):
        return '<Quote {}>'.format(self.values)


class OperatorQuote(AbstractSyntaxNode):
    """Represents the quote operator ' """
    def __repr__(self):
        return '<QuoteOP>'


class Symbol(AbstractSyntaxNode):
    """Represents a symbol (variable or function name)"""
    def __repr__(self):
        return '<Symb: {}>'.format(self.values[0])


class Literal(AbstractSyntaxNode):
    """Superclass of all values"""


class Int(Literal):
    """Represents an integer value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Float(Literal):
    """Represents a floating point value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Bool(Literal):
    """Represents a boolean value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class String(Literal):
    """Represents a character string"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Assign(AbstractSyntaxNode):
    """Represent the assignment of a value to a symbol

    Will be evaluated in a certain scope
    """
    def __repr__(self):
        if len(self.values) != 2:
            return '<Invalid Assign>'
        return '<Assign {} := {} >'.format(self.values[0], self.values[1])


class Car(AbstractSyntaxNode):
    """Represents the 'car' operation (returns first object in a list)"""
    def __init__(self, values, evaluable=True):
        """Throw exception if more or less than 1 argument is received

        :type values: tuple
        """
        if not isinstance(values, tuple):
            raise ASTError('Invalid initialization. Values must be a tuple')
        if len(values) != 1:
            raise syntax.LispySyntaxError(
                "Can only pass 1 argument to 'car'. {} given"
                .format(len(values))
            )
        # This can't be used in the constructor, because during the 1:1
        # translation, this will be broken. Must validate this however, so
        # let's make a method 'check_consistency' or smth, that can be checked
        # after the node is considered "committed"
        # if values[0].is_leaf():
        #     raise syntax.LispySyntaxError(
        #         "Can't apply 'car' to a simple atom. Need a list, but got {}"
        #         .format(values[0])
        #     )
        super(Car, self).__init__(values, evaluable)

    def __repr__(self):
        return '<CAR {}>'.format(self.values[0])


class ASTError(Exception):
    pass
