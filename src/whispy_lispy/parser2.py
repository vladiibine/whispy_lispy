# -*- coding utf-8 -*-
"""
Main function: `get_ast_from_cst` - call it with the output of the lexer
function `get_concrete_syntax_tree`
"""

from __future__ import unicode_literals, absolute_import
from whispy_lispy import ast, keywords, types


def internal_value_creator(internal_type):
    """Generic ast.Value creator.

    :param internal_type: an whispy_lispy.types object
    :return: a whispy_lispy.types.Value instance, wrapping the proper type
    """
    def wrapper(values):
        return ast.Value(tuple([internal_type(values)]))
    return wrapper


def determine_operation_type(cstree):
    """Determine the type of the new node

    :param whispy_lispy.cst.ConcreteSyntaxNode cstree: the CSTree
    """
    if cstree.is_root():
        return ast.RootAbstractSyntaxNode

    if not cstree.is_leaf():
        return ast.Apply
    else:
        if cstree.is_string():
            return internal_value_creator(types.String.from_quoted_values)
        if cstree.is_bool():
            return internal_value_creator(types.Bool)
        if cstree.is_int():
            return internal_value_creator(types.Int)
        if cstree.is_float():
            return internal_value_creator(types.Float)
        if cstree.is_operator():
            return ast.Operator
        if cstree.is_symbol():
            if cstree.symbol_equals(keywords.OPERATOR_QUOTE):
                return ast.QuoteShorthand
            if cstree.symbol_in_iterable(keywords.DEFINITION_ALIASES):
                return ast.Assign
            if cstree.symbol_in_iterable(keywords.CONDITION_ALIASES):
                return ast.Condition
            if cstree.symbol_equals(keywords.LAMBDA):
                return ast.Lambda
            return ast.Symbol

    raise Exception("Couldn't determine the operation type... failing now.")


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
        # better idea - scheme assumes an 'object' is the last thing in
        # the list. Do this transformation somewhere... should it perhaps be
        # a property of the list?
        if isinstance(child, ast.QuoteShorthand):
            skip_next = True
            new_children.append(
                container_cls((
                    ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
                    tree[idx + 1]
                ))
            )
            continue
        new_children.append(transform_quote_operator_into_function(
            child, container_cls=container_cls))
    return tree.alike(tuple(new_children))


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
            try:
                values.append(node_class(tuple(value.values)))
            except:
                operation_determiner(value)
                raise
        else:
            values.append(transform_one_to_one(value, operation_determiner))
    return operation_determiner(cstree)(tuple(values))


def pull_operations_up_inside_containers(astree, astype):
    """Returns a new astree, with a modified structure.

    Can be user to create any nodes which are represented in the CST
    as:
        Container:
            - Child: <desired_operation>
            - ...parameters*

    ... and in the AST as:
        <Desired_Operation>
            - ...parameters*

    :param ast.AbstractSyntaxNode astree: the tree to start with
    :param type astype: The type that's being pulled up
    :rtype: ast.AbstractSyntaxNode
    """
    if not isinstance(astree, ast.Container):
        return astree

    if not astree.values:
        return astree

    if isinstance(astree[0], astype):
        values = []
        for child in astree.values[1:]:
            values.append(pull_operations_up_inside_containers(child, astype))
        return astype(tuple(values))

    values = []
    for child in astree.values:
        values.append(pull_operations_up_inside_containers(child, astype))

    return astree.alike(tuple(values))


def get_ast_from_cst(cstree):
    """
    :param cst.ConcreteSyntaxNode cstree: the concrete syntax tree
    :rtype: ast.AbstractSyntaxNode
    """
    result = transform_one_to_one(cstree)

    # Here, all the operators should be transformed to function calls
    result = transform_quote_operator_into_function(result)
    result = pull_operations_up_inside_containers(result, ast.Assign)
    result = pull_operations_up_inside_containers(result, ast.Condition)
    result = pull_operations_up_inside_containers(result, ast.Lambda)
    return result
