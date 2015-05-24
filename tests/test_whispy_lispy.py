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

    def test_lexer_parses_all_known_symbol_types(self):
        self.assertEqual(
            lexer.get_tokens('dada 3.4 44 rere 6'),
            ['dada', 3.4, 44, 'rere', 6])

    def test_lexer_parses_simple_atom(self):
        self.assertEqual(lexer.get_tokens('(asdf 3)'), [['asdf', 3]])

    def test_lexer_omits_newline(self):
        self.assertEqual(lexer.get_tokens('asdf\nzxcv'), ['asdf', 'zxcv'])

    def test_lexer_parses_multiple_non_nested_atoms(self):
        self.assertEqual(
            lexer.get_tokens('(asdf 3) (zxcv 4)'),
            [['asdf', 3], ['zxcv', 4]])

    def test_lexer_parses_multiple_nested_atoms(self):
        self.assertEqual(
            lexer.get_tokens('(a 1 (2 3 (4 b)) c (2 2 (1 a))) (a 2)'),
            [['a', 1, [2, 3, [4, 'b']], 'c', [2, 2, [1, 'a']]], ['a', 2]]
        )
