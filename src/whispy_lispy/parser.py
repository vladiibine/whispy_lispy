# -*- coding utf-8 -*-
"""
DEPRECATED - will remove this module


Will accept a tree of allowed symbols, and construct an abstract syntax tree
"""
from __future__ import unicode_literals, absolute_import

from whispy_lispy import ast, cst, keywords


def get_ast(cstree):
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
    result = transform_car_function_to_builtin(result)
    result = make_quote_children_unevaluable(result)
    # Idea - the last transformation should transform all the remaining ASNodes
    # (but not subclass instances) into "lists"
    return result


def transform_car_function_to_builtin(tree):
    """Transform Apply(Car(), ...) to Car(...)

    :type tree: ast.AbstractSyntaxNode
    :rtype: ast.AbstractSyntaxNode
    """
    if tree.is_leaf():
        return tree

    if isinstance(tree, ast.Apply):
        if isinstance(tree[0], ast.Car):
            return transform_car_function_to_builtin(ast.Car(tree.values[1:]))  # noqa

    new_values = []
    for child in tree.values:
        new_values.append(transform_car_function_to_builtin(child))

    return tree.alike(tuple(new_values))


def make_quote_children_unevaluable(tree, met_quote=False):
    """AST Nodes need to know if they're evaluable or not.

    This function sets the property 'evaluable' to false to all the children
    of a quote

    :param bool met_quote: whether a quote was met higher up in the evaluation
        hierarchy (so this element is a child of a quote)
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


def transform_quote_operator_into_function(tree, container_cls=ast.Apply):
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
                    container_cls((ast.Quote((tree.values[idx + 1],)),)),
                    container_cls=container_cls),
            )
            continue
        new_children.append(transform_quote_operator_into_function(
            child, container_cls=container_cls))
    return tree.alike(tuple(new_children))


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
        if cstree.is_string():
            return ast.String
        if cstree.is_bool():
            return ast.Bool
        if cstree.is_int():
            return ast.Int
        if cstree.is_float():
            return ast.Float
        if cstree.is_symbol():
            if cstree.symbol_equals(keywords.OPERATOR_QUOTE):
                return ast.OperatorQuote
            if cstree.symbol_equals(keywords.BUILTIN_QUOTE_FUNC):
                return ast.Quote
            if cstree.symbol_equals(keywords.BUILTIN_CAR_FUNC):
                return ast.Car
            if cstree.symbol_equals(keywords.DEFINITION):
                return ast.Assign
            return ast.Symbol

    return ast.AbstractSyntaxNode


def transform_one_to_one(cstree,
                         operation_determiner=determine_operation_type):
    """Transform a concrete syntax tree into an abstract one, preserving the
    tree structure

    :type cstree: cst.ConcreteSyntaxNode
    :param operation_determiner: a function returning the class of the new node
    :rtype: ast.AbstractSyntaxNode
    """
    values = []
    if cstree.is_leaf():
        node_class = operation_determiner(cstree)
        return node_class(tuple(cstree.values))

    for value in cstree.values:
        if value.is_leaf():
            node_class = operation_determiner(value)
            values.append(node_class(tuple(value.values)))
        else:
            values.append(transform_one_to_one(value, operation_determiner))
    return operation_determiner(cstree)(tuple(values))
