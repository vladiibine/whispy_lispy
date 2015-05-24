# -*- coding utf-8 -*-
from __future__ import unicode_literals
import unittest
from whispy_lispy import parser
from whispy_lispy import ast


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
            parser.get_ast([['asdf', 3, 4]]), [ast.Apply(ast.Symbol('asdf'), ast.Literal(3), ast.Literal(4))])

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
