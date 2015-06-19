# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import six
from whispy_lispy import ast, types, cst, keywords

if six.PY2:
    str = unicode
else:
    unicode = str


def a_r(*value):
    """Return a RootAbstractSyntaxNode"""
    return _any_node(value, ast.RootAbstractSyntaxNode)


def a_v(value):
    """Return an ast.Value(types.<Proper type>(value))"""
    return ast.Value((
        {bool: types.Bool,
         int: types.Int,
         float: types.Float,
         unicode: types.String
         }.get(type(value))((value,)),))


def a_s(value):
    """Return an ast.Symbol"""
    return _any_node(value, ast.Symbol)


def _any_node(value, ntype):
    """Create the provided node type"""
    if isinstance(value, (tuple, list)):
        return ntype(tuple(value))
    return ntype((value,))


def a_li(*values):
    """Return an ast.List"""
    return _any_node(values, ast.Apply)


def a_la(*values):
    """Return an ast.Lambda"""
    return _any_node(values, ast.Lambda)


def a_a(*value):
    """Return an assignment"""
    return _any_node(value, ast.Assign)


def a_c(*values):
    """Return a condition"""
    return _any_node(values, ast.Condition)


def a_o(*values):
    """Return an AST operator"""
    return _any_node(values, ast.Operator)


def t_s(*values):
    """Return a types.Symbol node"""
    return _any_node(values, types.Symbol)


def t_i(*values):
    """return a types.Int node"""
    return _any_node(values, types.Int)


def t_b(*values):
    """return a types.Bool node"""
    return _any_node(values, types.Bool)

def t_f(*values):
    return _any_node(values, types.Float)

def t_str(*values):
    return _any_node(values, types.String)


def c_n(*values):
    """Return a Concrete Syntax node"""
    is_operator = values[0] in keywords.OPERATORS

    return cst.ConcreteSyntaxNode(values, is_operator)


def c_r(*values):
    """Return a Root concrete syntax tree"""
    return _any_node(values, cst.RootConcreteSyntaxnode)
