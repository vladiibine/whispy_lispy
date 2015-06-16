# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest

from whispy_lispy import lexer


class NonLispySyntaxTestCase(unittest.TestCase):
    def test_non_lispy_syntax_is_corrected(self):
        # sum(1 2 sum(3 4)) -> (sum 1 2 (sum 3 4))
        original_tokens = lexer.get_flat_token_list('sum(1 2 sum(3 4))')
        actual_tokens = lexer.make_parentheses_lispy(original_tokens)
        expected_tokens = lexer.get_flat_token_list('(sum 1 2 (sum 3 4))')

        self.assertEqual(actual_tokens, expected_tokens)
