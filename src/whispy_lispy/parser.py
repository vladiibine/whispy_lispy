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
    # TODO - transform >>> ' a b ...<<< into >>> (quote a) b ... <<< - no hurry
    # if not tree.is_leaf():
    #     new_children = []
    #     if isinstance(tree, ast.Quote2):
    #         iterable_values = tree.values[1:]
    #     else:
    #         iterable_values = tree.values
    #
    #     for child in iterable_values:
    #         new_children.append(mutate_tree_structure(child))
    #
    #     return tree.alike(tuple(new_children))
    # if isinstance(tree, ast.Apply2):
    #     if
    if not tree.is_leaf():
        new_children = []
        skip_next = False
        for idx, child in enumerate(tree.values):
            if skip_next:
                skip_next = False
                continue
            # Might be the case that the quote is the last element
            # Must throw some kind of error or something
            if isinstance(child, ast.OperatorQuote):
                skip_next = True
                new_children.append(
                    mutate_tree_structure(
                        ast.Apply2((ast.Quote2((tree.values[idx + 1], )),))))

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
        return node_class(tuple(cstree.values))

    for value in cstree.values:
        if value.is_leaf():
            node_class = determine_operation_type(value)
            values.append(node_class(tuple(value.values)))
        else:
            values.append(transform_one_to_one(value))
    return determine_operation_type(cstree)(tuple(values))


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
    else:
        if cstree.is_quote_function():
            return ast.Quote2
        if cstree.is_quote_literal():
            return ast.OperatorQuote

    # generic node that doesn't mean anything
    # When "everything" is implemented, reaching this section should raise
    # an exception - everything should be classifiable into a more meaningful
    # node type
    return ast.AbstractSyntaxNode
