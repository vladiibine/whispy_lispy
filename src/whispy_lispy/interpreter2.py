# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import

from whispy_lispy import ast, keywords, types, scopes2


def interpret_ast(astree, scope=None):
    """
    :param astree:
    :return:
    """
    result = None  # need some type for this
    if isinstance(astree, types.Type):
        return astree

    if scope is None:
        scope = scopes2.Scope()

    if astree.is_leaf() and not astree.is_root():
        return interpret_leaf(astree, scope)

    if isinstance(astree, ast.List):
        return interpret_list(astree, scope)

    for elem in astree.values:
        result = interpret_ast(elem, scope)

    return result


def interpret_leaf(astree, scope):
    if isinstance(astree, ast.Symbol):
        return scope[types.Symbol(astree.values)]  # Dereference symbol
    else:
        return astree[0]  # return the value


def interpret_symbol(symbol, scope):
    """
    :param ast.Symbol symbol: the symbol
    :param scopes2.Scope scope: the scope to interpret the symbol in
    :return:
    """
    # Here we return either the de-referenced value, or the symbol itself?
    # ATM only the de-referenced value
    return interpret_ast(symbol, scope)


def interpret_list(astree, scope):
    """Evaluate the list - if that should be done

    :param ast.AbstractSyntaxNode astree:
    :param scope:
    :return:
    """
    if astree[0].values[0] == keywords.DEFINITION:
        if isinstance(astree[2], ast.List):
            scope[types.Symbol(astree[1].values)] = interpret_ast(astree[2], scope)  # noqa
        elif isinstance(astree[2], ast.Literal):
            scope[types.Symbol(astree[1].values)] = interpret_ast(astree[2][0], scope)  # noqa
        elif isinstance(astree[2], ast.Symbol):
            scope[types.Symbol(astree[1].values)] = interpret_symbol(astree[2], scope)  # noqa
        return

    func = scope[types.Symbol(astree[0].values)]
    return func(*[interpret_ast(val, scope) for val in astree.values[1:]])
