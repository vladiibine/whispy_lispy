# -*- coding utf-8 -*-
"""
Will accept a tree of allowed symbols, and construct an abstract syntax tree
"""
from __future__ import unicode_literals, absolute_import

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
        node_class = determine_operation_type(cstree)
        return _commit_ast_node(cstree.values, node_class)

    for value in cstree.values:
        if value.is_leaf():
            node_class = determine_operation_type(value)
            values.append(_commit_ast_node(value.values, node_class))
        else:
            values.append(get_ast2(value))
    return _commit_ast_node(values, determine_operation_type(cstree))

def determine_operation_type(cstree):
    """Determine the operation type that this node corresponds to
    :param cstree:
    :return:
    """
    if cstree.is_root():
        return ast.RootAbstractSyntaxNode

    if not cstree.is_leaf():
        if cstree.values[0].is_symbol():
            return ast.Apply2

    # generic node that doesn't mean anything
    return ast.AbstractSyntaxNode


def _commit_ast_node(values, node_cls):
    """
    :param values:
    :return:
    """
    return node_cls(tuple(values))
