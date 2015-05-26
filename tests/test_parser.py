# -*- coding utf-8 -*-
from __future__ import unicode_literals
import unittest
import pytest

from whispy_lispy import parser, ast, cst


class ParserTests(unittest.TestCase):
    def test_parser_parses_empty_tree(self):
        self.assertEqual(parser.get_ast([]), [])

    def test_parser_parses_assignment(self):
        self.assertEqual(
            parser.get_ast([['def', 'x', 1]]), [ast.Assign('x', 1)]
        )

    def test_parser_parses_quotation(self):
        self.assertEqual(
            parser.get_ast([["'", 'a']]),
            [ast.Quote([ast.Symbol('a')])])

    def test_parses_explicit_evaluation(self):
        self.assertEqual(
            parser.get_ast([['eval', "'", ['a', 'b']]]),
            [ast.Eval(ast.Quote([ast.Apply(ast.Symbol('a'), ast.Symbol('b'))]))])  # noqa

    def test_parse_implicit_apply(self):
        self.assertEqual(
            parser.get_ast([['asdf', 3, 4]]),
            [ast.Apply(ast.Symbol('asdf'), ast.Literal(3), ast.Literal(4))])

    def test_parse_assigning_from_assigned_value(self):
        self.assertEqual(
            parser.get_ast([['def', 'x', 9], ['def', 'y', 'x']]),
            [ast.Assign('x', 9), ast.Assign('y', 'x')]
        )

    def test_quote_sum(self):
        result = parser.get_ast([["'", ['sum', 1, 2]]])
        self.assertEqual(
            result,
            [ast.Quote(
                [ast.Apply(ast.Symbol('sum'),
                           ast.Literal(1),
                           ast.Literal(2))])
             ]
        )

    def test_parse_eval_quote_sum(self):
        self.assertEqual(
            parser.get_ast([['eval', "'", ['sum', 1, 2]]]),
            [ast.Eval(
                ast.Quote(
                    [ast.Apply(
                        ast.Symbol('sum'),
                        ast.Literal(1),
                        ast.Literal(2))]))]
        )

def cn(val):
    """Return a ConcreteSyntaxNode """
    return create_any_node(val, cst.ConcreteSyntaxNode)

def rcn(val):
    """Return the root ConcreteSyntaxNode"""
    return create_any_node(val, cst.RootConcreteSyntaxnode)


def create_any_node(val, node_cls):
    if isinstance(val, tuple):
        return node_cls(val)
    else:
        return node_cls((val,))

def an(val):
    """Return an AbstractSyntaxNode """
    return create_any_node(val, ast.AbstractSyntaxNode)

def ran(val):
    """Return the root AbstractSyntaxNode"""
    return create_any_node(val, ast.RootAbstractSyntaxNode)


class Parser2TestCase(unittest.TestCase):
    def test_parses_empty_root_node(self):
        self.assertEqual(
            parser.translate_directly_cst_to_ast(rcn(())), ran(()))

    def test_parses_empty_non_root_node(self):
        self.assertEqual(
            parser.translate_directly_cst_to_ast(cn(())), an(()))

    def test_parses_non_empty_non_root(self):
        self.assertEqual(parser.translate_directly_cst_to_ast(cn(2)), an(2))

    def test_parses_single_element(self):
        self.assertEqual(
            parser.translate_directly_cst_to_ast(cn(cn(1))), an(an(1)))

    def test_parse_simple_nested_structure(self):
        self.assertEqual(
            parser.translate_directly_cst_to_ast(cn((cn('a'), cn(2)))),
            an((an('a'), an(2))))

    def test_parse_more_nested_structure(self):
        actual = parser.translate_directly_cst_to_ast(
            rcn((cn(1), cn((cn(2), cn((cn(3), cn(4), cn(5))))), cn(6))))
        expected = ran((an(1), an((an(2), an((an(3), an(4), an(5))))), an(6)))

        self.assertEqual(actual, expected)
