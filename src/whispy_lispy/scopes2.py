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
        return types.String((value,))

class OmniPresentScope(dict):
    """Provides the (non builtin) functions that are included in all scopes

    Provided functions:
    sum -> performs addition (on any number of numbers)
    sub -> subtraction (any number of numbers)
    simple_input -> returns one of the base values: string, bool, int, float
    print -> prints to standard output
    quit -> quits the session (
    """
    def __init__(self):
        # The sum function sums numbers
        def internal_sum(*nums):
            return python_value_to_internal_type(
                sum(num.values[0] for num in nums))

        self[types.Symbol(('sum',))] = internal_sum
        self[types.Symbol(('sub',))] = (
            lambda *nums: python_value_to_internal_type(
                reduce(sub, [num.values[0] for num in nums])))

        # the input can't yet return strings - we don't parse those yet, so
        # it can only return the types we know: float, int and bool
        def get_input():
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

        self[types.Symbol(('print',))] = print

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


class Scope(dict):
    def __init__(self, parent=None):
        if parent:
            super(Scope, self).__init__(parent)
        self.omni = OmniPresentScope()

    def __getitem__(self, item):
        try:
            if item in self.keys():
                return super(Scope, self).__getitem__(item)
            return self.omni[item]
        except KeyError:
            raise exceptions.UnboundSymbol(
                'Symbol "{}" can\'t be found in scope'.format(item)
            )
