# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import six
from whispy_lispy import ast, types


def a_r(*value):
    """Return a RootAbstractSyntaxNode"""
    return _any_node(value, ast.RootAbstractSyntaxNode)


def a_v(value):
    """Return an ast.Value(types.<Proper type>(value))"""
    return ast.Value((
        {bool: types.Bool,
         int: types.Int,
         float: types.Float,
         six.string_types: types.String
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
    return _any_node(values, ast.List)


def a_la(*values):
    """Return an ast.Lambda"""
    return _any_node(values, ast.Lambda)


def a_a(*value):
    """Return an assignment"""
    return _any_node(value, ast.Assign)


def a_c(*values):
    """Return a condition"""
    return _any_node(values, ast.Condition)


def t_s(*values):
    """Return a types.Symbol node"""
    return _any_node(values, types.Symbol)


def t_i(*values):
    """return a types.Int node"""
    return _any_node(values, types.Int)
