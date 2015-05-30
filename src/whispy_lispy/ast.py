# -*- coding utf-8 -*-
"""Abstract syntax tree stuff
"""
from __future__ import unicode_literals
import six

from whispy_lispy import exceptions


DEFINITION = 'def'
QUOTE = "'"
EVAL = "eval"

class Symbol(object):
    """Represents 'names' in a namespace... so functions or 'variables'
    """
    def __init__(self, value):
        self.value = value

    @staticmethod
    def matches(tree):
        if isinstance(tree, six.string_types):
            return tree

    @classmethod
    def from_match(cls, match):
        return cls(match)

    def __repr__(self):
        return 'Sym. {}'.format(self.value)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Symbol):
            return False
        return self.value == other.value

    def eval(self, scope):
        return self.value


class Literal(object):
    """Represents a direct value (int, and float for now) - will most likely
    add bool and list.

    Less likely, but probably, add some mappings.
    """
    def __init__(self, value):
        self.value = value

    @staticmethod
    def matches(tree):
        if tree is None:
            return
        if isinstance(tree, list):
            return
        return tree

    @classmethod
    def from_match(cls, match):
        return cls(match)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __repr__(self):
        return 'Lit. {}'.format(self.value)

    def eval(self, scope):
        return self.value


class Assign(object):
    """Represents the basic assignment.

    Right now only binds vars to the scope
    """
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Assign):
            return False
        return self.symbol == other.symbol and self.value == other.value

    @staticmethod
    def matches(tree):
        """Checks whether the tree is an assignment
        """
        if not tree:
            return

        if not isinstance(tree, list):
            return

        if len(tree) != 3:
            return

        if tree[0] != DEFINITION:
            return
        return tree[1], tree[2]

    @classmethod
    def from_match(cls, tree):
        return cls(*tree)

    def __repr__(self):
        return 'Assignment {} := {}'.format(self.symbol, self.value)

    def eval(self, scope):
        if isinstance(self.value, Symbol):
            value_eval = self.value.eval(scope)
            try:
                scope[self.symbol.eval(scope)] = scope[value_eval]
            except KeyError:
                raise exceptions.LispyUnboundSymbolError(
                    "No such symbol in scope: {}".format(value_eval)
                )
        elif isinstance(self.value, Literal):
            scope[self.symbol.eval(scope)] = self.value.eval(scope)


class Quote(object):
    """Stops the next expression from being evaluated
    """
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return 'Quote {}'.format(self.expression)

    @staticmethod
    def matches(tree):
        if not tree:
            return

        if not isinstance(tree, list):
            return

        if tree[0] == QUOTE:
            from whispy_lispy import parser
            return parser.get_ast(tree[1:])

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Quote):
            return False
        return self.expression == other.expression

    @classmethod
    def from_match(cls, elem):
        return cls(elem)

    def eval(self, scope):
        return self


class Eval(object):
    """Evaluates the next expression
    """
    def __init__(self, quotation):
        """
        :type quotation: Quote
        """

        self.quotation = quotation

    @staticmethod
    def matches(tree):
        if not tree:
            return

        if not isinstance(tree, list):
            return

        try:
            from whispy_lispy import parser
            quotation = parser.get_ast([tree[1:]])[0]
        except IndexError:
            return

        if not isinstance(quotation, Quote):
            # TODO - i wonder if this were a nice place to throw an error
            return
        if tree[0] == EVAL:
            return quotation

    @classmethod
    def from_match(cls, quotation):
        return cls(quotation)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Eval):
            return False
        return self.quotation == other.quotation

    def __repr__(self):
        return "Eval {}".format(self.quotation)

    def eval(self, scope):
        result = None
        for apply_candidate in self.quotation.expression:
            result = apply_candidate.eval(scope)

        return result



class Apply(object):
    def __init__(self, symbol, *args):
        if isinstance(symbol, six.string_types):
            pass
        self.symbol = symbol
        self.args = args

    @staticmethod
    def matches(tree):
        if not tree:
            return
        if not isinstance(tree, list):
            return

        # TODO - find nicer say to check for symbols that aren't values
        # By this i mean that the lexer must RETURN symbols and not strings
        if isinstance(tree[0], six.string_types):
            from whispy_lispy import parser
            return parser.get_ast(tree)

    @classmethod
    def from_match(cls, match):
        head, tail = match[0], match[1:]
        return cls(head, *tail)

    def __eq__(self, other):
        if other is None:
            return
        if not isinstance(other, Apply):
            return
        return self.symbol == other.symbol and self.args == other.args

    def __repr__(self):
        return 'Apply {} {}'.format(
            self.symbol, self.args if self.args is not None else '')

    def eval(self, scope):
        try:
            func = scope[self.symbol.eval(scope)]
        except KeyError:
            raise exceptions.LispyUnboundSymbolError(
                'Missing symbol name: "{}"'.format(self.symbol))
        return func(scope, self.args)

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


class Apply2(AbstractSyntaxNode):
    """Abstract apply"""
    __slots__ = ['values']

    def __repr__(self):
        return '<Apply {}>'.format(self.values)

class Quote2(AbstractSyntaxNode):
    """Abstract quote"""
    __slots__ = ['values']

    def __repr__(self):
        return '<Quote {}>'.format(self.values)

class OperatorQuote(AbstractSyntaxNode):
    """Represents the quote operator ' """
    __slots__ = ['values']

    def __repr__(self):
        return '<QuoteOP>'