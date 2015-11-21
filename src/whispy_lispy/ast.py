# -*- coding utf-8 -*-
"""Abstract syntax tree stuff
"""
from __future__ import unicode_literals
from whispy_lispy import types


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


class Lambda(Container):
    """Represents the expression that creates a lambda function"""
    def __repr__(self):
        return '<Lambda at {}>'.format(id(self))


class QuoteShorthand(AbstractSyntaxNode):
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
        return '<Value {}>'.format(self.values)


class Int(Value):
    """Represents an integer value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])

    @classmethod
    def from_parsed_result(cls, *args, **kwargs):
        return types.Int((int(args[2][0]),))


class Float(Value):
    """Represents a floating point value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])

    @classmethod
    def from_parsed_result(cls, *args, **kwargs):
        return types.Float((float(''.join(args[2])),))


class Bool(Value):
    """Represents a boolean value"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])

    @classmethod
    def from_parsed_result(cls, *args, **kwargs):
        return types.Bool((True if args[2][0] == '#t' else False,))


class String(Value):
    """Represents a character string"""
    def __repr__(self):
        return '<{}>'.format(self.values[0])

    @classmethod
    def from_parse_result(cls, *args, **kwargs):
        quoted_string = args[2][0]
        return types.String((quoted_string[1:-1],))


class Assign(Container):
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


class Condition(Container):
    """The condition node
    (cond
        (condition1 result1)
        (condition2 result2)
        ...
        (#t fallback_result)
    )
    """
    def __repr__(self):
        return '<Cond X {cond_count}: {conditions}>'.format(
            cond_count=len(self.values),
            conditions=self.values
        )


class Apply(Container):
    """The abstract list"""
    def __repr__(self):
        return '<List :{}>'.format(self.values)


class Operator(Container):
    """Represents any one of the operators"""
    def __repr__(self):
        return '<Operator {}>'.format(self.values)
