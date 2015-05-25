# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from whispy_lispy import lexer
from whispy_lispy import syntax
from whispy_lispy import cst

def like_tokens(obj):
    """Wraps all the objects in the nested list (or the single object) with
    a cst.Token
    """
    if not isinstance(obj, list):
        return cst.Token(obj)

    result = []
    for elem in obj:
        if not isinstance(elem, list):
            result.append(cst.Token(elem))
        else:
            result.append(like_tokens(elem))

    return result

class BaseLexerTestCase(unittest.TestCase):
    def assertEqualTokens(self, second, first, msg=None):
        """Like assertEqual, but wraps all the values with a cst.Token before
        comparing equality - because the lexer returns cst.Tokens and not
        raw python values now
        """
        return self.assertEqual(second, like_tokens(first), msg)


class LexerTestCase(BaseLexerTestCase):

    def test_lexer_parses_empty_text(self):
        self.assertEqualTokens(lexer.get_tokens(''), [])

    def test_lexer_parses_int(self):
        self.assertEqualTokens(lexer.get_tokens('1'), [1])

    def test_lexer_parses_float(self):
        self.assertEqualTokens(lexer.get_tokens('1.4'), [1.4])

    def test_lexer_parses_symbol(self):
        self.assertEqualTokens(lexer.get_tokens('as_df'), ['as_df'])

    def test_lexer_parses_all_known_symbol_types(self):
        self.assertEqualTokens(
            lexer.get_tokens('d 3.4 44 r 6'), ['d', 3.4, 44, 'r', 6])

    def test_lexer_parses_simple_atom(self):
        self.assertEqualTokens(lexer.get_tokens('(a 3)'), [['a', 3]])

    def test_lexer_omits_newline(self):
        self.assertEqualTokens(lexer.get_tokens('a\nz'), ['a', 'z'])

    def test_lexer_parses_symbol_then_atom(self):
        self.assertEqualTokens(lexer.get_tokens('a (1 d)'), ['a', [1, 'd']])

    def test_lexer_parses_atom_then_symbol(self):
        self.assertEqualTokens(lexer.get_tokens('(a 1) 3'), [['a', 1], 3])

    def test_lexer_parses_multiple_non_nested_atoms(self):
        self.assertEqualTokens(lexer.get_tokens('(a 3) (z 4)'), [['a', 3], ['z', 4]])  # noqa

    def test_lexer_parses_multiple_nested_atoms(self):
        self.assertEqualTokens(
            lexer.get_tokens('(a 1 (2 3 (4 b)) c (2 2 (1 a))) (a 2)'),
            [['a', 1, [2, 3, [4, 'b']], 'c', [2, 2, [1, 'a']]], ['a', 2]]
        )

    def test_lexer_blows_up_on_single_opening_paren_outside_atom(self):
        self.assertRaises(syntax.LispySyntaxError, lexer.get_tokens, '(')

    def test_lexer_blows_up_on_extra_closing_paren_outside_atom(self):
        self.assertRaises(syntax.LispySyntaxError, lexer.get_tokens, 'a (1) )')

    def test_lexer_blows_up_on_mismatched_parens(self):
        self.assertRaises(syntax.LispySyntaxError, lexer.get_tokens, '(a ( b ) (')  # noqa

    def test_lexer_blows_up_when_closing_parens_in_the_beginning(self):
        self.assertRaises(syntax.LispySyntaxError, lexer.get_tokens, ') a (b c)')  # noqa

    def test_lexer_blows_up_on_deeply_nested_non_matching_parentheses(self):
        self.assertRaises(
            syntax.LispySyntaxError, lexer.get_tokens, '(a b (c (d ))))('
        )

    def test_lexer_matches_quote(self):
        # self.assertTrue(lexer.get_tokens("'''a b"), ["'", "'", "'", "a", "b"])
        self.assertEqualTokens(lexer.get_tokens("'''a b"), ["'", "'", "'", "a", "b"])  # noqa

    # These next tests are just to see the basic structure of the syntax tree

    def test_lexer_packs_assignment(self):
        self.assertEqualTokens(lexer.get_tokens('(def x 1)'), [['def', 'x', 1]])  # noqa

    def test_parses_eval_quote(self):
        self.assertEqualTokens(
            lexer.get_tokens("(eval '(a b))"), [['eval', "'", ['a', 'b']]])

    def test_parse_assignment_from_assigned_value(self):
        self.assertEqualTokens(
            lexer.get_tokens("(def x 9) (def y x)"),
            [['def', 'x', 9], ['def', 'y', 'x']]
        )

    def test_parse_eval_quote(self):
        self.assertEqualTokens(
            lexer.get_tokens("(eval '(sum 1 2))"),
            [[u'eval', u"'", [u'sum', 1, 2]]]
        )

class FlatLexerTestCase(BaseLexerTestCase):
    def _create_token(self, value):
        return cst.Token([value])

    def test_parses_empty_text(self):
        self.assertEqual(lexer.get_flat_token_list(''), [])

    def test_parses_known_types(self):
        self.assertEqual(
            lexer.get_flat_token_list('a 2 4.4 b #t #f'), [
                cst.Token(['a']),
                cst.Token([2]),
                cst.Token([4.4]),
                cst.Token(['b']),
                cst.Token([True]),
                cst.Token([False])]
        )

    def test_parses_nested_known_types(self):
        t = self._create_token
        i = cst.IncrementNesting
        d = cst.DecrementNesting

        self.assertEqual(
            lexer.get_flat_token_list(
                '(a b) (#f d) (e f (g (h 1 2)))'),
            [i, t('a'), t('b'), d, i, t(False), t('d'), d, i, t('e'),
             t('f'), i, t('g'), i, t('h'), t(1), t(2), d, d, d]
        )

    def test_omits_newline(self):
        t = self._create_token
        i = cst.IncrementNesting
        d = cst.DecrementNesting

        self.assertEqual(
            lexer.get_flat_token_list('\n\na\nb\n(1\n 2\n)'),
            [t('a'), t('b'), i, t(1), t(2), d])

    def test_accepts_non_matching_parentheses(self):
        t = self._create_token
        i = cst.IncrementNesting
        d = cst.DecrementNesting

        self.assertEqual(
            lexer.get_flat_token_list('))a b ))('),
            [
                d, d, t('a'), t('b'), d, d, i
            ]
        )
