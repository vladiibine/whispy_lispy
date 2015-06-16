# -*- coding utf-8 -*-
from __future__ import unicode_literals

# export all constants in this module
__all__ = [elem for elem in dict(globals()) if elem.isupper()]

OPERATORS = [
    '+', '-', '*', '**', '%', '/', '//', '>', '>=', '<', '<=', '=', '==', '<<',
    '>>', '!=', '&', '|', '^', '~', 'and', 'or', 'xor', 'not', 'eqv'
]

DEFINITION = 'def'
DEFINITION_ALIASES = ['def', 'define']

CONDITION_ALIASES = ['cond', 'if']

LAMBDA = 'lambda'

OPERATOR_QUOTE = '\''

BUILTIN_QUOTE_FUNC = 'quote'
BUILTIN_CAR_FUNC = 'car'
