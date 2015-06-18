# -*- coding: utf-8 -*-
"""All the builtin operations (operators) are defined here

Also, for the moment, some builtin functions will also be defined here
"""
from __future__ import unicode_literals, print_function
import six
import sys
import operator

from whispy_lispy import keywords, types


def to_python(value):
    """Converts Whispy Lispy types to python types """
    if isinstance(value, bool):
        return types.Bool((value,))
    if isinstance(value, int):
        return types.Int((value,))
    if isinstance(value, float):
        return types.Float((value,))
    if isinstance(value, six.string_types):
        return types.String.from_quoted_values(value)


def to_internal(value):
    """Converts Python types to Whispy Lispy types"""
    return value.values[0]

# Many operators can be unary, so (<operator> single_value) will succeed
# This value means that the unary operator will compare the object to itself
VALUE_SELF_REFERENCE = object()
# This value means that the operator is not unary
NO_DEFAULT_VALUE = object()


class Operator(object):
    """Template for creating Whispy Lispy operations from Python operators

    Operators in Python don't work exactly as their intended analogues in
    Whispy Lispy. For instance `reduce(operators.eq, ["asdf"]` will return
    "asdf" in python.

    We'd like this to return True in Whispy Lispy, because this operation
    is reflective (don't know if that's a word)
    For the same reason, the '>' operation applied to only one value should
    always return False. In Python it again returns the value
    """
    def __init__(self, operator_, default_value=VALUE_SELF_REFERENCE):
        """
        :param operator_: a python operator from module operator.*
        :param default_value: a value to be used as the default for this
        operator
        """

        self.operator = operator_
        self.default = default_value

    def __call__(self, interpreter, scope, *values):
        if self.default is VALUE_SELF_REFERENCE:
            # The list can't be empty. Should have blown up at the AST
            values += (values[0],)
        elif self.default is not NO_DEFAULT_VALUE:
            values += (self.default,)

        return to_python(
            reduce(
                self.operator,
                (to_internal(interpreter(val, scope)) for val in values)))


def internal_sum(interpreter, scope, *nums):
    """
    :param interpreter: the interpreter2.interpret_ast function or
        something that interprets the *nums list
    :param scope: a scope (usually dict)
    :param nums: internal numbers to add
    :return:
    """
    try:
        return to_python(
            sum(
                to_internal(interpreter(num, scope))
                for num in nums)
        )
    except:
        raise


def internal_sub(interpreter, scope, *nums):
    return to_python(
        reduce(operator.sub,
               [to_internal(interpreter(val, scope))
                for val in nums])
    )


def get_input(interpreter, scope, *values):
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
    return to_python(result)


builtin_print = lambda i, s, *args: print(*args)


def operation_quit(interpreter, scope, *args):
    """Just quits and avoids funny values"""
    print('Thank you! Come again!')
    if args:
        if isinstance(args[0], types.Int):
            sys.exit(int(to_internal(args[0])))
        else:
            print(args[0])
            sys.exit(1)
    sys.exit()


OPERATIONS = dict(zip(
    keywords.OPERATORS, [None] * 11 + [Operator(operator.eq)] + [None] * 13))
