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
        self.assertEqual(lexer.get_tokens('d 3.4 44 r 6'), ['d', 3.4, 44, 'r', 6])  # noqa

    def test_lexer_parses_simple_atom(self):
        self.assertEqual(lexer.get_tokens('(a 3)'), [['a', 3]])

    def test_lexer_omits_newline(self):
        self.assertEqual(lexer.get_tokens('a\nz'), ['a', 'z'])

    def test_lexer_parses_symbol_then_atom(self):
        self.assertEqual(lexer.get_tokens('a (1 d)'), ['a', [1, 'd']])

    def test_lexer_parses_atom_then_symbol(self):
        self.assertEqual(lexer.get_tokens('(a 1) 3'), [['a', 1], 3])

    def test_lexer_parses_multiple_non_nested_atoms(self):
        self.assertEqual(lexer.get_tokens('(a 3) (z 4)'), [['a', 3], ['z', 4]])

    def test_lexer_parses_multiple_nested_atoms(self):
        self.assertEqual(
            lexer.get_tokens('(a 1 (2 3 (4 b)) c (2 2 (1 a))) (a 2)'),
            [['a', 1, [2, 3, [4, 'b']], 'c', [2, 2, [1, 'a']]], ['a', 2]]
        )

    def test_lexer_blows_up_on_single_opening_paren_outside_atom(self):
        self.assertRaises(lexer.LispySyntaxError, lexer.get_tokens, '(')

    def test_lexer_blows_up_on_extra_closing_paren_outside_atom(self):
        self.assertRaises(lexer.LispySyntaxError, lexer.get_tokens, 'a (1) )')

    def test_lexer_blows_up_on_mismatched_parens(self):
        self.assertRaises(lexer.LispySyntaxError, lexer.get_tokens, '(a ( b ) (')  # noqa

    def test_lexer_blows_up_when_closing_parens_in_the_beginning(self):
        self.assertRaises(lexer.LispySyntaxError, lexer.get_tokens, ') a (b c)')  # noqa

    def test_lexer_blows_up_on_deeply_nested_non_matching_parentheses(self):
        self.assertRaises(
            lexer.LispySyntaxError, lexer.get_tokens,
            '(a b (c (d ))))('
        )
