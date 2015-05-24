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
