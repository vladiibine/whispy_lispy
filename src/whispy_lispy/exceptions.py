# -*- coding utf-8 -*-
"""Defines the internal base exceptions for whispy lispy"""

class BaseWhispyLispyError(Exception):
    pass


class WhispyLispySyntaxError(BaseWhispyLispyError):
    pass


class UnboundSymbol(BaseWhispyLispyError):
    pass

class EvaluationError(BaseWhispyLispyError):
    pass