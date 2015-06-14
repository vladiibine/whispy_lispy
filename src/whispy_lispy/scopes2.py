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


class OmniPresentScope(dict):
    """Provides the builtin functions that are included in all scopes

    Provided functions:
    sum -> performs addition (on any number of numbers)
    sub -> subtraction (any number of numbers)
    simple_input -> returns one of the base values: string, bool, int, float
    print -> prints to standard output
    quit -> quits the session (
    """
    def __init__(self):
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

        self[types.Symbol(('sum',))] = internal_sum

        def internal_sub(interpreter, scope, *nums):
            return python_value_to_internal_type(
                reduce(sub,
                       [internal_value_to_python_type(interpreter(val, scope))
                        for val in nums])
            )
        self[types.Symbol(('sub',))] = internal_sub

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

        self[types.Symbol(('simple_input',))] = get_input

        self[types.Symbol(('print',))] = lambda i, s, *args: print(*args)

        def quit(*args):
            """Just quits and avoids funny values"""
            print('Thank you! Come again!')
            if args:
                if isinstance(args[0], int):
                    sys.exit(int(args[0]))
                else:
                    print(args[0])
                    sys.exit(1)
            sys.exit()

        self[types.Symbol(('quit',))] = quit

omni_scope = OmniPresentScope()


class Scope(dict):
    def __init__(self, parent=None, omni=omni_scope):
        """
        :param dict parent: the parent scope
        """
        super(Scope, self).__init__()
        self.parent = parent if parent is not None else {}
        self.omni = omni

    def __getitem__(self, item):
        if item in self:
            return super(Scope, self).__getitem__(item)

        ancestor = getattr(self, 'parent', None)
        while ancestor is not None:
            if item in ancestor:
                return ancestor[item]
            ancestor = getattr(ancestor, 'parent', None)

        if item in self.omni:
            return self.omni[item]

        raise exceptions.UnboundSymbol(
            'Symbol "{}" can\'t be found in scope'.format(item)
        )


class FunctionScope(Scope):
    """Scope that looks for symbols among the formal parameters"""
    def __init__(self, param_names=None, arguments=None,
                 parent=None, omni=omni_scope):
        if param_names:
            self.local_scope = dict(zip(param_names, arguments))
        else:
            self.local_scope = {}
        super(FunctionScope, self).__init__(parent, omni)

    def __getitem__(self, item):
        if item in self.local_scope:
            return self.local_scope[item]
        return super(FunctionScope, self).__getitem__(item)
