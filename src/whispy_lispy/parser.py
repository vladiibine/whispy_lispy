# -*- coding utf-8 -*-
"""
Will accept a tree of allowed symbols, and construct an abstract syntax tree
"""
from __future__ import unicode_literals, absolute_import
from collections import deque

from whispy_lispy import ast, cst


def get_ast(tree):
    """

    :param tree: A Syntax tree(?) - anyway a possibly nested list produced
        by the lexer
    :return: an abstract syntax tree
    """
    abstract_syntax_tree = []
    if not tree:
        return abstract_syntax_tree

    for elem in tree:
        for operation in (ast.Assign, ast.Quote, ast.Eval, ast.Symbol, ast.Literal, ast.Apply):  # noqa
            match = operation.matches(elem)
            if match is not None:
                abstract_syntax_tree.append(operation.from_match(match))
                break

    return abstract_syntax_tree


def get_ast2(cstree):
    """Convert the concrete syntax tree into an abstract one

    :type cstree: cst.ConcreteSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    q = deque([[]])


    return ast.AbstractSyntaxNode(())
