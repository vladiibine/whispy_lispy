# -*- coding utf-8 -*-
"""
Main function: `interpret_ast` - call it with the output from the parser
function `get_ast_from_cst`
"""
from __future__ import unicode_literals, absolute_import

from whispy_lispy import ast, types, scopes2


def interpret_ast(astree, scope=None):
    """Main interpreter activity

    :param ast.AbstractSyntaxNode astree:
    :rtype: types.Type
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

    if isinstance(astree, ast.Assign):
        return interpret_assign(astree, scope)

    if isinstance(astree, ast.Condition):
        return interpret_condition(astree, scope)

    if isinstance(astree, ast.Lambda):
        return interpret_lambda(astree, scope)

    for elem in astree.values:
        result = interpret_ast(elem, scope)

    return result


def interpret_lambda(astree, scope):
    return create_function(astree, scope, is_lambda=True)


def interpret_condition(astree, scope):
    for value in astree.values:
        condition = value[0]
        if interpret_ast(condition, scope) == types.Bool((True,)):
            return interpret_ast(value[1], scope)


def interpret_assign(astree, scope):
    # Simple symbol assignment
    if isinstance(astree[0], ast.Symbol):
        scope[types.Symbol(astree[0].values)] = interpret_ast(astree[1], scope)

    # Function assignment
    elif isinstance(astree[0], ast.List):
        # first: assume it contains a single value - means no formal parameters
        scope_key = types.Symbol(astree[0].values[0].values)
        new_function = create_function(astree, scope)
        scope[scope_key] = new_function


def create_function(astree, scope, is_lambda=False):
    # For a normal definition, the first node in the list is the function name
    # For a lambda, the list starts with the arguments
    start_idx = 0 if is_lambda else 1

    params = tuple(
        [types.Symbol(elem.values) for elem in astree[0].values[start_idx:]])

    return types.Function((
        # the function name
        types.String(astree[0].values[0].values if not is_lambda else ('lambda',)),  # noqa
        # the formal parameter names
        params,
        astree[1],  # The AST that should be interpreted
        scope
    ))


def interpret_leaf(astree, scope):
    if isinstance(astree, ast.Symbol):
        return scope[types.Symbol(astree.values)]  # Dereference symbol
    else:
        return astree[0]  # return the value


def interpret_list(astree, scope):
    """Evaluate the list - if that should be done

    :param ast.AbstractSyntaxNode astree:
    :param scope:
    :return:
    """
    func = obtain_function(astree[0], scope)
    result = func(interpret_ast, scope,
                  *[interpret_ast(val, scope) for val in astree.values[1:]])
    return result


def obtain_function(astree, scope):
    """
    :param ast.AbstractSyntaxNode astree: a symbol, or expression evaluating to
        a function
    :rtype: types.Function
    """
    if isinstance(astree, ast.Symbol):
        return scope[types.Symbol((astree[0],))]
    elif isinstance(astree, ast.Container):
        return interpret_ast(astree, scope)

    raise Exception("Couldn't get the function you specified:")
