# -*- coding utf-8 -*-
"""
Will accept a tree of allowed symbols, and construct an abstract syntax tree
"""
from __future__ import unicode_literals, absolute_import

from whispy_lispy import ast, cst, keywords


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

    :type tree: ast.AbstractSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    result = transform_quote_operator_into_function(tree)
    result = transform_quote_function_into_builtin(result)
    result = transform_assignment_symbol_to_builtin(result)
    result = make_quote_children_unevaluable(result)
    # Idea - the last transformation should transform all the remaining ASNodes
    # (but not subclass instances) into "lists"
    return result


def make_quote_children_unevaluable(tree, met_quote=False):
    """AST Nodes need to know if they're evaluable or not.

    This function sets the property 'evaluable' to false to all the children
    of a quote

    :type tree: ast.AbstractSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    if tree.is_leaf():
        return tree.alike(tree.values, not met_quote)

    new_values = []

    for child in tree.values:
        new_values.append(make_quote_children_unevaluable(
            child.alike(
                child.values,
                not (met_quote or isinstance(tree, ast.Quote))),
            met_quote or isinstance(tree, ast.Quote)
        ))

    return tree.alike(tuple(new_values), not met_quote)


def transform_quote_function_into_builtin(tree):
    """Converts Apply(Quote(), X, ...) into Quote(X, ...)

    This step makes determining the children of a Quote much easier
    """
    if tree.is_leaf():
        return tree

    if isinstance(tree, ast.Apply):
        if isinstance(tree[0], ast.Quote):
            return transform_quote_function_into_builtin(ast.Quote(tree.values[1:]))  # noqa

    new_values = []
    for child in tree.values:
        new_values.append(transform_quote_function_into_builtin(child))

    return tree.alike(tuple(new_values))


def transform_assignment_symbol_to_builtin(tree):
    """Convert Apply(Assign('x', 'y')) into Assign('x', 'y')

    ATM we assume the syntax is correct. Should probably do a check for syntax
    errors at some point after conversion, or in this very function.

    :param ast.AbstractSyntaxNode tree: the ast to transform
    :rtype: ast.AbstractSyntaxNode
    """
    if tree.is_leaf():
        return tree

    if isinstance(tree, ast.Apply):
        if isinstance(tree[0], ast.Assign):
            return transform_assignment_symbol_to_builtin(ast.Assign(tree.values[1:]))  # noqa

    new_values = []
    for child in tree.values:
        new_values.append(transform_assignment_symbol_to_builtin(child))

    return tree.alike(tuple(new_values))


def transform_quote_operator_into_function(tree):
    """Transform  (' a b ...) into  ((quote a) b ...) """
    if tree.is_leaf():
        return tree

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
                transform_quote_operator_into_function(
                    ast.Apply((ast.Quote((tree.values[idx + 1], )),))))
            continue
        new_children.append(transform_quote_operator_into_function(child))
    return tree.alike(tuple(new_children))


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
    :param cst.ConcreteSyntaxNode cstree: a concrete syntax tree
    :rtype: type
    """
    if cstree.is_root():
        return ast.RootAbstractSyntaxNode

    if not cstree.is_leaf():
        if cstree.values[0].is_symbol():
            return ast.Apply
    else:
        if cstree.is_quote_function():
            return ast.Quote
        if cstree.is_quote_literal():
            return ast.OperatorQuote
        if cstree.is_bool():
            return ast.Bool
        if cstree.is_int():
            return ast.Int
        if cstree.is_float():
            return ast.Float
        if cstree.is_symbol():
            if cstree.symbol_equals(keywords.DEFINITION):
                return ast.Assign
            return ast.Symbol

    # generic node that doesn't mean anything
    # When "everything" is implemented, reaching this section should raise
    # an exception - everything should be classifiable into a more meaningful
    # node type
    return ast.AbstractSyntaxNode
