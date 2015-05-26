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
    return translate_directly_cst_to_ast(cstree)


def translate_directly_cst_to_ast(cstree):
    """Transforms the CSNode elements directly into ASNodes, keeping the
    structure of the tree intact

    :type cstree: cst.ConcreteSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    values = []
    is_root = cstree.is_root()
    if cstree.is_leaf():
        return _commit_ast_node(is_root, cstree.values)
    for value in cstree.values:
        if value.is_leaf():
            values.append(ast.AbstractSyntaxNode(value.values))
        else:
            values.append(translate_directly_cst_to_ast(value))
    return _commit_ast_node(is_root, values)


def _commit_ast_node(is_root, values):
    """
    :type is_root: bool
    :param values:
    :return:
    """
    if is_root:
        return ast.RootAbstractSyntaxNode(tuple(values))
    else:
        return ast.AbstractSyntaxNode(tuple(values))
