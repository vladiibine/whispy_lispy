# -*- coding utf-8 -*-
"""Integration-ish tests
"""
from __future__ import absolute_import, unicode_literals

import unittest

from whispy_lispy import lexer, parser, interpreter

SAMPLE_SUM_NUMBERS = """\
(def a 3)
(def b 4)
(def x (sum a b))
8
"""


class IntegrationTestCase(unittest.TestCase):
    def test_sum_3_numbers(self):
        scope = {'sum': lambda *nums: sum(nums)}
        cst = lexer.get_concrete_syntax_tree(
            lexer.get_flat_token_list(SAMPLE_SUM_NUMBERS)
        )
        ast = parser.get_ast2(cst)
        result = interpreter.interpret_ast(ast, scope)

        self.assertEqual(scope['x'], 7)
        self.assertEqual(result, 8)
