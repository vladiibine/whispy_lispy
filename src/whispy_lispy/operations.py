# -*- coding: utf-8 -*-
"""All the builtin operations (operators) are defined here

Also, for the moment, some builtin functions will also be defined here
"""
from __future__ import unicode_literals, print_function
import six
import sys
import operator

from whispy_lispy import keywords, types


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


class Operator(object):
    def default_value(self, *args):
        pass

    def __call__(self, interpreter, scope, *args):
        pass


class Equal(Operator):
    def __call__(self, interpreter, scope, *values):
        try:
            return python_value_to_internal_type(
                reduce(operator.eq,
                       (internal_value_to_python_type(interpreter(val, scope))
                        for val in values)))
        except:
            raise


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


def internal_sub(interpreter, scope, *nums):
    return python_value_to_internal_type(
        reduce(operator.sub,
               [internal_value_to_python_type(interpreter(val, scope))
                for val in nums])
    )


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


builtin_print = lambda i, s, *args: print(*args)


def operation_quit(interpreter, scope, *args):
    """Just quits and avoids funny values"""
    print('Thank you! Come again!')
    if args:
        if isinstance(args[0], types.Int):
            sys.exit(int(internal_value_to_python_type(args[0])))
        else:
            print(args[0])
            sys.exit(1)
    sys.exit()


OPERATIONS = zip(
    keywords.OPERATORS, [None] * 11 + [Equal()] + [None] * 13)
