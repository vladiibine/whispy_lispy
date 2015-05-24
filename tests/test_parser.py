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
        self.assertEqual(parser.get_ast([["'", 'a']]), [ast.Quote('a')])

    def test_parses_explicit_evaluation(self):
        self.assertEqual(
            parser.get_ast([['eval', "'", ['a', 'b']]]),
            [ast.Eval(ast.Quote(['a', 'b']))])

    def test_parse_implicit_apply(self):
        self.assertEqual(
            parser.get_ast([['asdf', 3, 4]]), [ast.Apply('asdf', 3, 4)])
