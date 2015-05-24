# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from whispy_lispy import lexer

class LexerTestCase(unittest.TestCase):
    def test_lexer_parses_empty_text(self):
        self.assertEqual(lexer.get_tokens(''), [])

    def test_lexer_parses_int(self):
        self.assertEqual(lexer.get_tokens('1'), [1])

    def test_lexer_parses_float(self):
        self.assertEqual(lexer.get_tokens('1.4'), [1.4])

    def test_lexer_parses_symbol(self):
        self.assertEqual(lexer.get_tokens('as_df'), ['as_df'])
