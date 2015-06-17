# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from whispy_lispy import lexer
from whispy_lispy import cst
from ..constructors import *
import whispy_lispy.exceptions


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


# For easily instantiating the nodes, and tokens
def n(value):
    """Return an ConcreteSyntaxNode """
    return create_node_type(value, cst.ConcreteSyntaxNode)


def rn(value):
    """Return the root ConcreteSyntaxNode """
    return create_node_type(value, cst.RootConcreteSyntaxnode)


def create_node_type(value, node_cls):
    if isinstance(value, tuple):
        return node_cls(value)
    else:
        return node_cls((value,))

t = cst.Token
d = cst.DecrementNesting()
i = cst.IncrementNesting()


class FlatLexerTestCase(BaseLexerTestCase):
    def test_parses_empty_text(self):
        self.assertEqual(lexer.get_flat_token_list(''), [])

    def test_parses_known_types(self):
        self.assertSequenceEqual(
            lexer.get_flat_token_list(r'a 2 4.4 b #t #f "as\"df"'), [
                t('a'),
                t(2),
                t(4.4),
                t('b'),
                t(True),
                t(False),
                t(r'"as\"df"')])

    def test_parses_multiline_strings(self):
        tokens = lexer.get_flat_token_list(r'''
        "a
        \"b
        c"
        ''')
        expected_value = '"a\n        \\"b\n        c"'
        self.assertEqual(tokens, [t(expected_value)])

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
        self.assertEqual(lexer.get_concrete_syntax_tree([]), rn(()))

    def test_single_element(self):
        self.assertEqual(
            lexer.get_concrete_syntax_tree([t('_a')]),
            rn(n('_a'))
        )

    def test_simple_atom(self):
        self.assertEqual(
            lexer.get_concrete_syntax_tree([i, t('a_'), t('b'), d]),
            rn(n((n('a_'), n('b'))))
        )

    def test_2_top_level_nodes_and_2_level_nesting(self):
        self.assertEqual(
            # (define x (+ 1 2)) 4
            lexer.get_concrete_syntax_tree(
                [i, t('def'), t('x'), i, t('sum'), t(1), t(2), d, d, t(4)]
            ),
            rn((n((n('def'), n('x'), n((n('sum'), n(1), n(2))))), n(4)))
        )

    def test_5_nesting_levels_and_2_outmost_nodes(self):
        actual = lexer.get_concrete_syntax_tree(
                # 4 (define x (+ 5 4 ((lambda (x) (+ 3 x))1)))
                [t(4), i, t('def'), t('z'), i, t('sum'), t(5), t(6), i, i, t('lambda'), i, t('x'), d, i, t('sum'), t(7), t('y'), d, d, t(1), d, d, d]  # noqa
            )

        expected = rn((
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
            whispy_lispy.exceptions.WhispyLispySyntaxError,
            lexer.get_concrete_syntax_tree,
            [i]
        )

    def test_blow_up_on_too_few_opening_parentheses(self):
        self.assertRaises(
            whispy_lispy.exceptions.WhispyLispySyntaxError,
            lexer.get_concrete_syntax_tree,
            [d]
        )

    def test_syntax_error_when_parentheses_mismatch(self):
        self.assertRaises(
            whispy_lispy.exceptions.WhispyLispySyntaxError,
            lexer.get_concrete_syntax_tree,
            [d, t(0), i]
        )

    def test_produces_lists_with_literals_on_first_position(self):
        self.assertEqual(
            lexer.get_concrete_syntax_tree([i, t(1), d]),
            cst.RootConcreteSyntaxnode((
                cst.ConcreteSyntaxNode((
                    cst.ConcreteSyntaxNode((1,)),)),)))

    def test_alphanumeric_names(self):
        self.assertEqual(
            lexer.get_flat_token_list('f1__a444_a'),
            [cst.Token('f1__a444_a')]
        )

    def test_weird_character_combinations(self):
        self.assertRaises(
            whispy_lispy.exceptions.WhispyLispySyntaxError,
            lexer.get_flat_token_list,
            'f1__a. 444_a')

    def test_not_so_weird_character_combination(self):
        self.assertEqual(
            lexer.get_flat_token_list('1.1 1.1 1.1 1.1'),
            [t_f(1.1), t_f(1.1), t_f(1.1), ]
        )
