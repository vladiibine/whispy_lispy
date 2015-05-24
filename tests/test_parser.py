# -*- coding utf-8 -*-
from __future__ import unicode_literals
import unittest
from whispy_lispy import parser

class ParserTests(unittest.TestCase):
    def test_parser_parses_empty_tree(self):
        self.assertEqual(parser.get_ast([]), [])

    def test_parser_parses_assignment(self):
        self.assertEqual(
            parser.get_ast([['def', 'x', 1]]),
            [parser.Assign('x', 1)]
        )

    def test_parser_parses_quotation(self):
        self.assertEqual(parser.get_ast([["'", 'a']]), [parser.Quote('a')])

    def test_parses_explicit_evaluation(self):
        self.assertEqual(
            parser.get_ast([['eval', "'", ['a', 'b']]]),
            [parser.Eval(parser.Quote(['a', 'b']))])

    def test_parse_implicit_apply(self):
        self.assertEqual(
            parser.get_ast([['asdf', 3, 4]]), [parser.Apply('asdf', 3, 4)])
