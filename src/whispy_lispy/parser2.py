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
from whispy_lispy import parser, ast, keywords


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
    result = transform_quote_operator_into_function(result)
    return result
