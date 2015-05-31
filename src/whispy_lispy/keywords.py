# -*- coding utf-8 -*-
from __future__ import unicode_literals as _ul

# export all constants in this module
__all__ = [elem for elem in dict(globals()) if elem.isupper()]

DEFINITION = 'def'

OPERATOR_QUOTE = '\''

BUILTIN_QUOTE_FUNC = 'quote'
BUILTIN_CAR_FUNC = 'car'