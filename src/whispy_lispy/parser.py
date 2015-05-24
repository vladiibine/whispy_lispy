# -*- coding utf-8 -*-
"""
Will accept a tree of allowed symbols, and construct an abstract syntax tree
"""
from __future__ import unicode_literals

DEFINITION = 'def'
QUOTE = "'"
EVAL = "eval"

class Assignment(object):
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Assignment):
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


class Eval(object):
    def __init__(self, quotation):
        self.quotation = quotation

    @staticmethod
    def matches(tree):
        if not tree:
            return

        if not isinstance(tree, list):
            return

        quotation = get_ast([tree[1:]])[0]
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




def get_ast(tree):
    """

    :param tree: A Syntax tree(?) - anyway a possibly nested list produced
        by the lexer
    :return: an abstract syntax tree
    """
    ast = []
    if not tree:
        return ast

    for elem in tree:
        for operation in (Assignment, Quote, Eval):
            match = operation.matches(elem)
            if match:
                ast.append(operation.from_match(match))
                break

    return ast
