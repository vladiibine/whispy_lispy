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
            return False
        if len(tree) != 3:
            return False
        if tree[0] != DEFINITION:
            return False
        return True

    @classmethod
    def from_tree(cls, tree):
        return cls(tree[1], tree[2])

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
        return tree[0] == QUOTE

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Quote):
            return False
        return self.value == other.value

    @classmethod
    def from_tree(cls, elem):
        return cls(elem[1])


class Eval(object):
    def __init__(self, func):
        self.func = func

    @staticmethod
    def matches(tree):
        if not tree:
            return False
        if len(tree) != 2:
            return False
        if tree[0] == EVAL:
            return True

    @classmethod
    def from_tree(cls, tree):
        return cls(tree[1])

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Eval):
            return False
        return self.func == other.func

    def __repr__(self):
        return "Eval {}".format(self.func)




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
            if operation.matches(elem):
                ast.append(operation.from_tree(elem))

        # if Assignment.is_assignment(elem):
        #     ast.append(Assignment.from_tree(elem))
        # if Quote.is_quote(elem):
        #     ast.append(Quote.from_tree(elem))
        # if Eval.is_eval(elem):
        #     ast.append(Eval.from_tree(elem))

    return ast
