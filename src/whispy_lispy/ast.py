# -*- coding utf-8 -*-
from __future__ import unicode_literals

from whispy_lispy import syntax, exceptions


DEFINITION = 'def'
QUOTE = "'"
EVAL = "eval"


class Assign(object):
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
        if hasattr(self.value, 'eval'):
            scope[self.symbol] = self.value.eval(scope)
        elif isinstance(self.value, syntax.Symbol):
            try:
                scope[self.symbol] = scope[self.value]
            except KeyError:
                raise exceptions.LispyUnboundSymbolError
        else:
            # TODO - drop this when the parser will only return AST classes
            scope[self.symbol] = self.value


class Quote(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Quote {}'.format(self.value)

    @staticmethod
    def matches(tree):
        if not tree:
            return False

        if not isinstance(tree, list):
            return False

        if tree[0] == QUOTE:
            return tree[1]

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Quote):
            return False
        return self.value == other.value

    @classmethod
    def from_match(cls, elem):
        return cls(elem)

    def eval(self, scope):
        return self


class Eval(object):
    def __init__(self, quotation):
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
        pass


class Apply(object):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    @staticmethod
    def matches(tree):
        if not tree:
            return
        if not isinstance(tree, list):
            return

        # TODO - find nicer say to check for symbols that aren't values
        # By this i mean that the lexer must RETURN symbols and not strings
        if isinstance(tree[0], syntax.Symbol):
            return tree

    @classmethod
    def from_match(cls, match):
        head, tail = match[0], match[1:]
        return cls(head, *tail)

    def __eq__(self, other):
        if other is None:
            return
        if not isinstance(other, Apply):
            return
        return self.func == other.func and self.args == other.args

    def __repr__(self):
        return 'Apply {} {}'.format(
            self.func, self.args if self.args is not None else '')

    def eval(self, scope):
        pass
