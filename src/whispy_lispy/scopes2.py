# -*- coding utf-8 -*-
"""Defines the scope objects"""
from __future__ import absolute_import, print_function, unicode_literals

import sys
import six
from operator import sub

from whispy_lispy import exceptions, types

if six.PY3:
    raw_input = input
    from functools import reduce


def python_value_to_internal_type(value):
    if isinstance(value, int):
        return types.Int((value,))
    elif isinstance(value, float):
        return types.Float((value,))
    elif isinstance(value, bool):
        return types.Bool((value,))
    elif isinstance(value, six.string_types):
        return types.String.from_quoted_values(value)


def internal_value_to_python_type(value):
    return value.values[0]


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
        self.vals = {}

        # The sum function sums numbers
        def internal_sum(interpreter, scope, *nums):
            """
            :param interpreter: the interpreter2.interpret_ast function or
                something that interprets the *nums list
            :param scope: a scope (usually dict)
            :param nums: internal numbers to add
            :return:
            """
            try:
                return python_value_to_internal_type(
                    sum(
                        internal_value_to_python_type(interpreter(num, scope))
                        for num in nums)
                )
            except:
                raise

        self.vals[types.Symbol(('sum',))] = internal_sum

        def internal_sub(interpreter, scope, *nums):
            return python_value_to_internal_type(
                reduce(sub,
                       [internal_value_to_python_type(interpreter(val, scope))
                        for val in nums])
            )
        self.vals[types.Symbol(('sub',))] = internal_sub

        def get_input(interpreter, scope):
            """
            :rtype: str| float | int | bool | None
            """
            # Hardcode the message, because we don't have strings yet
            user_input = raw_input('input: ')

            # float?
            if '.' in user_input:
                try:
                    return types.Float((float(user_input),))
                except ValueError:
                    pass
            # int?
            try:
                return types.Int((int(user_input),))
            except ValueError:
                pass

            # bool?
            result = (True if user_input == '#t' else
                      False if user_input == '#f' else None)
            # string?
            if result is None:
                result = '"{}"'.format(user_input)
            return python_value_to_internal_type(result)

        self.vals[types.Symbol(('simple_input',))] = get_input

        self.vals[types.Symbol(('print',))] = lambda i, s, *args: print(*args)

        def quit(interpreter, scope, *args):
            """Just quits and avoids funny values"""
            print('Thank you! Come again!')
            if args:
                if isinstance(args[0], types.Int):
                    sys.exit(int(internal_value_to_python_type(args[0])))
                else:
                    print(args[0])
                    sys.exit(1)
            sys.exit()

        self.vals[types.Symbol(('quit',))] = quit

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
