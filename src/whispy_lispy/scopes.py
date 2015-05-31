# -*- coding utf-8 -*-
"""Defines the scope objects"""
from __future__ import absolute_import, unicode_literals, print_function

from operator import sub


class OmniPresentScope(dict):
    """Provides the (non builtin) functions that are included in all scopes

    Provided functions:
    sum -> performs addition (on any number of numbers)
    sub -> subtraction (any number of numbers)
    simple_input -> returns one of the base values: string, bool, int, float
    print -> prints to standard output
    """
    def __init__(self):
        # The sum function sums numbers
        self['sum'] = lambda *nums: sum(nums)
        # Subtraction
        self['sub'] = lambda *nums: reduce(sub, nums)

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
                    return float(user_input)
                except ValueError:
                    pass
            # int?
            try:
                return int(user_input)
            except ValueError:
                pass

            # bool?
            result = (True if user_input == '#t' else
                      False if user_input == '#f' else None)
            # string?
            if result is None:
                result = '"{}"'.format(user_input)
            return result

        self['simple_input'] = get_input

        self['print'] = print


class Scope(dict):
    def __init__(self, parent=None):
        if parent:
            super(Scope, self).__init__(parent)
        self.omni = OmniPresentScope()

    def __getitem__(self, item):
        if item in self.keys():
            return super(Scope, self).__getitem__(item)
        return self.omni[item]
