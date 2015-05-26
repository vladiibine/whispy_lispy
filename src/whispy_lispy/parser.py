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
    values = []

    if cstree.is_leaf():
        return _commit_ast_node(cstree, cstree.values)

    for value in cstree.values:
        if value.is_leaf():
            values.append(ast.AbstractSyntaxNode(value.values))
        else:
            values.append(get_ast2(value))

    return _commit_ast_node(cstree, values)

def _commit_ast_node(cstree, values):
    if cstree.is_root():
        return ast.RootAbstractSyntaxNode(tuple(values))
    else:
        return ast.AbstractSyntaxNode(tuple(values))


# Obsolete function, but it broke py.test during the tests, so i'll keep
# it as an example.
def get_ast_that_breaks_py_test(cstree):
    """Convert the concrete syntax tree into an abstract one

    :type cstree: cst.ConcreteSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    values = []

    for value in cstree.values:
        values.append(value)

    if cstree.is_root():
        return ast.RootAbstractSyntaxNode(tuple(values))
    else:
        return ast.AbstractSyntaxNode(tuple(values))
