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
            [parser.Assignment('x', 1)]
        )

    def test_parser_parses_quotation(self):
        self.assertEqual(parser.get_ast([["'", 'a']]), [parser.Quote('a')])

    def test_parser_parses_evaluation(self):
        self.assertEqual(parser.get_ast([['eval', 'x']]), [parser.Eval('x')])
