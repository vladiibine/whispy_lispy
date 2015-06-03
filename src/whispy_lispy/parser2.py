# -*- coding utf-8 -*-
"""New idea for the parser: Return a data structure that's actually the
code itself (return a native nested list of function calls)

Of course something like this:
1 2 3
...won't be evaluated like
(1 2 3)
because the top level list is special
"""

from __future__ import unicode_literals, absolute_import
from whispy_lispy import parser, ast, keywords, types


def determine_operation_type(cstree):
    """Determine the type of the new node
    """
    if cstree.is_root():
        return ast.RootAbstractSyntaxNode

    if not cstree.is_leaf():
        return ast.List
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


def get_ast_from_cst(cstree):
    """
    :param cst.ConcreteSyntaxNode cstree: the concrete syntax tree
    :rtype: ast.AbstractSyntaxNode
    """
    result = parser.transform_one_to_one(cstree, determine_operation_type)

    # Here, all the operators should be transformed to function calls
    result = transform_quote_operator_into_function(result)
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

