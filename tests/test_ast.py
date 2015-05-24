# -*- coding utf-8 -*-
from __future__ import unicode_literals
import unittest

from whispy_lispy import ast

class QuoteTestCase(unittest.TestCase):
    def test_quote_single_value(self):
        self.assertEqual(
            ast.Quote.matches(["'", 'a']),
            [ast.Symbol('a')]
        )

class ApplyTestCase(unittest.TestCase):
    def test_simple_apply(self):
        self.assertEqual(
            ast.Apply.matches(['su', 1, 2]),
            [ast.Symbol('su'), ast.Literal(1), ast.Literal(2)]
        )
