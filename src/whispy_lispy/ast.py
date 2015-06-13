# -*- coding utf-8 -*-
"""Abstract syntax tree stuff
"""
from __future__ import unicode_literals


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


class Container(AbstractSyntaxNode):
    """Marks that this node contains other nodes"""


class RootAbstractSyntaxNode(Container):
    """The abstract node marking the root of the node hierarchy"""
    def __repr__(self):
        return '<RaN {}>'.format(self.values)


class Apply(Container):
    """Abstract apply"""
    def __repr__(self):
        return '<Apply {}>'.format(self.values)


class Quote(Container):
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


class Value(AbstractSyntaxNode):
    """Superclass of all values"""
    def __repr__(self):
        return '<Literal {}>'.format(self.values)


class Int(Value):
    """Represents an integer value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Float(Value):
    """Represents a floating point value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Bool(Value):
    """Represents a boolean value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class String(Value):
    """Represents a character string"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])


class Assign(AbstractSyntaxNode):
    """Represent the assignment of a value to a symbol

    Syntax: `(def A B)`

    Assignments are expressions, their return value is null.
    `A` can be a symbol, or list.
    If it's a list, it should be a flat list of symbols.
    The list isn't evaluated "normally", so anything other than symbols in it
    will not get evaluated, and will simply be ignored (like a comment one
    could say)

    If `A` is a symbol, it will become a variable in the current
    scope. It it's a list (a b c...), the first symbol in it will become
    a function in the scope, and its parameter list will be the remaining
    symbols in A, namely (b c ...)

    The second argument, `B` can be any expression and will always be
    evaluated.

    Will be evaluated in a certain scope
    """
    def __repr__(self):
        if len(self.values) != 2:
            return '<Invalid Assign>'
        return '<Assign {} := {} >'.format(self.values[0], self.values[1])


class List(Container):
    """The abstract list"""
    def __repr__(self):
        return '<List :{}>'.format(self.values)
