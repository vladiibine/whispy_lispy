# -*- coding utf-8 -*-
"""
Main function: `get_ast_from_cst` - call it with the output of the lexer
function `get_concrete_syntax_tree`
"""

from __future__ import unicode_literals, absolute_import
from whispy_lispy import ast, keywords, types


def literal_creator(internal_type):
    """Generic ast.Value creator.

    :param internal_type: an whispy_lispy.types object
    :return:
    """
    def wrapper(values):
        return ast.Value(tuple([internal_type(values)]))
    return wrapper


def determine_operation_type(cstree):
    """Determine the type of the new node
    """
    if cstree.is_root():
        return ast.RootAbstractSyntaxNode

    if not cstree.is_leaf():
        return ast.List
    else:
        if cstree.is_string():
            return literal_creator(types.String.from_quoted_values)
        if cstree.is_bool():
            return literal_creator(types.Bool)
        if cstree.is_int():
            return literal_creator(types.Int)
        if cstree.is_float():
            return literal_creator(types.Float)
        if cstree.is_symbol():
            if cstree.symbol_equals(keywords.OPERATOR_QUOTE):
                return ast.OperatorQuote
            if cstree.symbol_equals(keywords.DEFINITION):
                return ast.Assign
            return ast.Symbol


def transform_quote_operator_into_function(tree, container_cls=ast.List):
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
        if isinstance(child, ast.OperatorQuote):
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
            values.append(node_class(tuple(value.values)))
        else:
            values.append(transform_one_to_one(value, operation_determiner))
    return operation_determiner(cstree)(tuple(values))


def create_proper_assignment_nodes(astree):
    """Creates Assignment nodes

    This is important, because the assignment operation is more lower level
    than a function call. Otherwise, we'd have problems with expressions like
    `(define (f x) 1)`. This would try to evaluate (f x) before the definition
    took place.

    Previously:
        Node: List
          - Child: Symbol 'def'
          - ...Children

    After this transformation:
        Node: Assign
          - ...Children

    :param ast.AbstractSyntaxNode astree: the tree to start with
    :rtype: ast.AbstractSyntaxNode
    """
    if not isinstance(astree, ast.Container):
        return astree

    if isinstance(astree[0], ast.Assign):
        values = []
        for child in astree.values[1:]:
            values.append(create_proper_assignment_nodes(child))
        return ast.Assign(tuple(values))

    values = []
    for child in astree.values:
        values.append(create_proper_assignment_nodes(child))

    return astree.alike(tuple(values))


def get_ast_from_cst(cstree):
    """
    :param cst.ConcreteSyntaxNode cstree: the concrete syntax tree
    :rtype: ast.AbstractSyntaxNode
    """
    result = transform_one_to_one(cstree)

    # Here, all the operators should be transformed to function calls
    result = transform_quote_operator_into_function(result)
    result = create_proper_assignment_nodes(result)
    return result


AST_TO_SIMPLE_INTERNAL_TYPES_MAP = {
    ast.Int: types.Int,
    ast.Float: types.Float,
    ast.String: types.String,
    ast.Bool: types.Bool,
    ast.Symbol: types.Symbol
}

AST_NESTED_TYPES_TO_INTERNAL_TYPES_MAP = {
    ast.List: types.List,
    ast.RootAbstractSyntaxNode: tuple
}


def get_native_types_from_ast(astree):
    """Return the abstract syntax tree translated to the internal types

    :param ast.AbstractSyntaxNode astree: an AST
    :rtype: tuple[types.Type] | types.Type
    """
    new_values = []

    new_simple_type = AST_TO_SIMPLE_INTERNAL_TYPES_MAP.get(type(astree))
    if new_simple_type is not None:
        return new_simple_type(astree.values)

    new_nested_type = AST_NESTED_TYPES_TO_INTERNAL_TYPES_MAP.get(type(astree))
    if new_nested_type:
        for child in astree.values:
            new_values.append(get_native_types_from_ast(child))
        return new_nested_type(tuple(new_values))
