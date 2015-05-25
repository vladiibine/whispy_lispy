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


# leaving this here as a model - for some weird reason
@unittest.skip
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


# For easily instantiating the nodes, and tokens
def n(value):
    if isinstance(value, tuple):
        return cst.Node(value)
    else:
        return cst.Node((value,))

t = cst.Token
d = cst.DecrementNesting
i = cst.IncrementNesting


class FlatLexerTestCase(BaseLexerTestCase):
    def test_parses_empty_text(self):
        self.assertEqual(lexer.get_flat_token_list(''), [])

    def test_parses_known_types(self):
        self.assertSequenceEqual(
            lexer.get_flat_token_list('a 2 4.4 b #t #f'), [
                t('a'),
                t(2),
                t(4.4),
                t('b'),
                t(True),
                t(False)])

    def test_parses_nested_known_types(self):
        self.assertSequenceEqual(
            lexer.get_flat_token_list(
                '(a b) (#f d) (e f (g (h 1 2)))'),
            [i, t('a'), t('b'), d, i, t(False), t('d'), d, i, t('e'),
             t('f'), i, t('g'), i, t('h'), t(1), t(2), d, d, d]
        )

    def test_omits_newline(self):
        self.assertSequenceEqual(
            lexer.get_flat_token_list('\n\t   \na\t\t\nb\n\n  \n(1\n   2\n)'),
            [t('a'), t('b'), i, t(1), t(2), d])

    def test_parses_quote(self):
        self.assertSequenceEqual(
            lexer.get_flat_token_list("(def x '(a 1 2))"),
            [i, t('def'), t('x'), t('\''), i, t('a'), t(1), t(2), d, d]
        )

    def test_accepts_non_matching_parentheses(self):
        self.assertSequenceEqual(
            lexer.get_flat_token_list('))a b ))('),
            [d, d, t('a'), t('b'), d, d, i])


class ConcreteSyntaxTreeTestCase(unittest.TestCase):
    def test_empty_token_list(self):
        self.assertEqual(lexer.get_concrete_syntax_tree([]), cst.Node(()))

    def test_single_element(self):
        self.assertEqual(
            lexer.get_concrete_syntax_tree([t('_a')]),
            n(n('_a'))
        )

    def test_simple_atom(self):
        self.assertEqual(
            lexer.get_concrete_syntax_tree([i, t('a_'), t('b'), d]),
            n(n((n('a_'), n('b'))))
        )

    def test_2_top_level_nodes_and_2_level_nesting(self):
        self.assertEqual(
            # (define x (+ 1 2)) 4
            lexer.get_concrete_syntax_tree(
                [i, t('def'), t('x'), i, t('sum'), t(1), t(2), d, d, t(4)]
            ),
            n((n((n('def'), n('x'), n((n('sum'), n(1), n(2))))), n(4)))
        )

    def test_5_nesting_levels_and_2_outmost_nodes(self):
        actual = lexer.get_concrete_syntax_tree(
                # 4 (define x (+ 5 4 ((lambda (x) (+ 3 x))1)))
                [t(4), i, t('def'), t('z'), i, t('sum'), t(5), t(6), i, i, t('lambda'), i, t('x'), d, i, t('sum'), t(7), t('y'), d, d, t(1), d, d, d]  # noqa
            )

        expected = n((
            n(4),
            n((
                n('def'),
                n('z'),
                n((
                    n('sum'),
                    n(5),
                    n(6),
                    n((
                        n((
                            n('lambda'),
                            n(n('x')),
                            n((
                                n('sum'),
                                n(7),
                                n('y'))),
                        )),
                        n(1)
                    ))))))))
        self.assertEqual(actual, expected)

    def test_blow_up_if_too_few_closing_parentheses(self):
        self.assertRaises(
            syntax.LispySyntaxError,
            lexer.get_concrete_syntax_tree,
            [i]
        )

    def test_blow_up_on_too_few_opening_parentheses(self):
        self.assertRaises(
            syntax.LispySyntaxError,
            lexer.get_concrete_syntax_tree,
            [d]
        )

    def test_syntax_error_when_parentheses_mismatch(self):
        self.assertRaises(
            syntax.LispySyntaxError,
            lexer.get_concrete_syntax_tree,
            [d, t(0), i]
        )
