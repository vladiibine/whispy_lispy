# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest

from whispy_lispy import lexer


class NonLispySyntaxTestCase(unittest.TestCase):
    """Currently, there is experimental (and highly buggy) support
    for the non-lisp-like syntax for function calls that instead of
    using `(func arg1 arg2 ...)`, uses `func(arg1 arg2 ...)`.

    Although this works for calling simple builtin functions, and even
    for simple variable assignment, lambdas and defining functions, don't
    work.

    Probably work won't continue too much here.
    """
    def test_non_lispy_syntax_is_corrected(self):
        # sum(1 2 sum(3 4)) -> (sum 1 2 (sum 3 4))
        original_tokens = lexer.get_flat_token_list('sum(1 2 sum(3 4))')
        actual_tokens = lexer.make_parentheses_lispy(original_tokens)
        expected_tokens = lexer.get_flat_token_list('(sum 1 2 (sum 3 4))')

        self.assertEqual(actual_tokens, expected_tokens)
