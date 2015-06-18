# -*- coding: utf-8 -*-
"""All the builtin operations (operators) are defined here

Also, for the moment, some builtin functions will also be defined here
"""
from __future__ import unicode_literals, print_function
import six
import sys
import operator
import itertools

from whispy_lispy import keywords, types, exceptions


if six.PY3:
    unicode = str


def to_internal(value):
    """Convert Python types to Whispy Lispy types """
    if isinstance(value, bool):
        return types.Bool((value,))
    if isinstance(value, int):
        return types.Int((value,))
    if isinstance(value, float):
        return types.Float((value,))
    if isinstance(value, six.string_types):
        return types.String((value,))


def to_python(value):
    """Converts Whispy Lispy types to Python types """
    return value.values[0]

# Many operators can be unary, so (<operator> single_value) will succeed
# This value means that the unary operator will compare the object to itself
VALUE_SELF_REFERENCE = object()
# This defines the neutral values for addition
ADDITION_NEUTRAL_VALUES = {
    int: 0, float: 0.0, unicode: '', bool: True}
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
    def __init__(self, operator_,
                 default_value=VALUE_SELF_REFERENCE,
                 type_fallbacks={},
                 incompatible_types=lambda *args: False):
        """
        :param operator_: a python operator from module operator.*
        :param dict default_value: a value to be used as the default for this
        operator
        :param dict[type, str|unicode] type_fallbacks: For the provided
            parameter types, use these operators instead
        :param incompatible_types: lambda that takes a set of python types
            and returns True if they can't be considered compatible in the
            context of this operator
        """
        self.type_fallbacks = type_fallbacks
        self.operator = operator_
        self.defaults_dict = default_value
        self.incompatible_types_check = incompatible_types

    def __call__(self, interpreter, scope, *values):
        if self.defaults_dict is VALUE_SELF_REFERENCE:
            # The list can't be empty. Should have blown up at the AST
            processable_values = values + (values[0],)
        elif self.defaults_dict is not NO_DEFAULT_VALUE:
            processable_values = values + (
                to_internal(
                    self.defaults_dict[type(to_python(values[0]))]),)
        else:
            processable_values = values

        iter_for_type_check, iter_for_reduce = itertools.tee(
            to_python(interpreter(val, scope)) for val in processable_values)

        types = set(type(item) for item in iter_for_type_check)
        # Addition specific logic - should extract it to method(maybe reusable)
        if len(types) > 1:
            if types != {int, float}:
                raise exceptions.EvaluationError(
                    'Incompatible types: {}'.format(processable_values)
                )

        # TODO - extract this logic nicely
        # if self.incompatible_types_check(types):
        #     raise exceptions.EvaluationError(
        #         'Incompatible types: {}'.format(processable_values)
        #     )

        # Generic logic - can stay
        values_type = types.pop()
        if values_type in self.type_fallbacks:
            return OPERATIONS[self.type_fallbacks[values_type]](interpreter,
                                                                scope, *values)

        return to_internal(
            reduce(self.operator, iter_for_reduce))


def internal_sum(interpreter, scope, *nums):
    """
    :param interpreter: the interpreter2.interpret_ast function or
        something that interprets the *nums list
    :param scope: a scope (usually dict)
    :param nums: internal numbers to add
    :return:
    """
    try:
        return to_internal(
            sum(
                to_python(interpreter(num, scope))
                for num in nums)
        )
    except:
        raise


def internal_sub(interpreter, scope, *nums):
    return to_internal(
        reduce(operator.sub,
               [to_python(interpreter(val, scope))
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
    return to_internal(result)


builtin_print = lambda i, s, *args: print(*args)


def operation_quit(interpreter, scope, *args):
    """Just quits and avoids funny values"""
    print('Thank you! Come again!')
    if args:
        if isinstance(args[0], types.Int):
            sys.exit(int(to_python(args[0])))
        else:
            print(args[0])
            sys.exit(1)
    sys.exit()


OPERATIONS = dict(zip(
    keywords.OPERATORS,
    [Operator(
        operator.add,
        ADDITION_NEUTRAL_VALUES,
        {bool: 'or'},
    )] +
    [None] * 10 +
    [Operator(operator.eq)] +
    [None] * 9 +
    [Operator(operator.or_)] +
    [None] * 13))
