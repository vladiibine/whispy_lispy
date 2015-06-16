# -*- coding utf-8 -*-
"""Defines the scope objects"""
from __future__ import absolute_import, print_function, unicode_literals

import sys
import six
from operator import sub

from whispy_lispy import exceptions, types, operations

if six.PY3:
    raw_input = input
    from functools import reduce


class OmniPresentScope(object):
    """Provides the builtin functions that are included in all scopes

    Provided functions:
    sum -> performs addition (on any number of numbers)
    sub -> subtraction (any number of numbers)
    simple_input -> returns one of the base values: string, bool, int, float
    print -> prints to standard output
    quit -> quits the session (
    """
    def __init__(self):
        self.vals = {
            types.Symbol(('sum',)): operations.internal_sum,
            types.Symbol(('sub',)): operations.internal_sub,
            types.Symbol(('simple_input',)): operations.get_input,
            types.Symbol(('print',)): operations.builtin_print,
            types.Symbol(('quit',)): operations.operation_quit}

    def __getitem__(self, item):
        return self.vals[item]

    def __contains__(self, item):
        return item in self.vals

omni_scope = OmniPresentScope()


class Scope(object):
    def __init__(self, parent=None, omni=omni_scope):
        """
        :param dict | Scope parent: the parent scope
        """
        self.vals = {}
        self.parent = parent if parent is not None else {}
        self.omni = omni

    def __getitem__(self, item):
        if item in self.vals:
            return self.vals[item]

        try:
            return self.parent[item]
        except KeyError:
            pass

        if item in self.omni:
            return self.omni[item]

        raise exceptions.UnboundSymbol(
            'Symbol "{}" can\'t be found in scope'.format(item)
        )

    def __contains__(self, item):
        return (item in self.vals or
                item in self.parent or
                item in self.omni)

    def __setitem__(self, key, value):
        self.vals[key] = value


class FunctionScope(Scope):
    """Scope that looks for symbols among the formal parameters and in
    the closure scope
    """
    def __init__(self, param_names=None, arguments=None,
                 parent=None, closure_scope=None, omni=omni_scope):

        self.closure_scope = closure_scope or {}
        if param_names:
            self.local_scope = dict(zip(param_names, arguments))
        else:
            self.local_scope = {}
        super(FunctionScope, self).__init__(parent, omni)

    def __getitem__(self, item):
        if item in self.local_scope:
            return self.local_scope[item]
        if item in self.closure_scope:
            return self.closure_scope[item]
        return super(FunctionScope, self).__getitem__(item)

    def __contains__(self, item):
        if item in self.closure_scope or item in self.local_scope:
            return True

        return super(FunctionScope, self).__contains__(item)
