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

    result = transform_one_to_one(cstree)
    return mutate_tree_structure(result)

def mutate_tree_structure(tree):
    """Apply transformations to the abstract syntax tree that alter its
    structure

    I wonder if this is really necessary... I mean just replace the quote
    with an Apply('quote', X), and we can keep the structure, and just mutate
    one element "'" -> "quote"...we'll see

    :type tree: ast.AbstractSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    if not tree.is_leaf():
        new_children = []
        if isinstance(tree, ast.Quote2):
            iterable_values = tree.values[1:]
        else:
            iterable_values = tree.values

        for child in iterable_values:
            new_children.append(mutate_tree_structure(child))

        return tree.alike(tuple(new_children))

    return tree


def transform_one_to_one(cstree):
    """Transform a concrete syntax tree into an abstract one, preserving the
    tree structure

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
        if cstree.values[0].is_quote():
            return ast.Quote2
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
