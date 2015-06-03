# -*- coding utf-8 -*-
from __future__ import unicode_literals

import unittest

from whispy_lispy import parser2, cst, ast

i = cst.IncrementNesting
d = cst.DecrementNesting
cn = cst.ConcreteSyntaxNode
an = ast.AbstractSyntaxNode

class Parser2TestCase(unittest.TestCase):
    def test_simple_list_is_created(self):
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn(('a',)),
                )),
            )))

        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((ast.List((ast.Symbol(('a',)),)),)))

    def test_transform_simple_quote_operator_into_function(self):
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((cn(('\'',)), cn(('a',)))))

        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.List((ast.Symbol(('quote',)),
                          ast.Symbol(('a',)))),)))

    def test_transform_2_non_nested_quote_operators_into_function_calls(self):
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn(('\'',)),
                cn(('a',)),
                cn((1,)),
                cn(('\'',)),
                cn(('b',)))))
        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.List((ast.Symbol(('quote',)), ast.Symbol(('a',)))),
                ast.Int((1,)),
                ast.List((ast.Symbol(('quote',)), ast.Symbol(('b',)))),
            )))

    def transform_3_nested_quote_operators_into_function_calls(self):
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn(('\'',)), cn(('\'',)), cn(('\'',)), cn(('a',))
            )))
        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.List((
                    ast.Symbol(('quote',)),
                    ast.List((
                        ast.Symbol(('quote',)),
                        ast.List((
                            ast.Symbol(('quote',)),
                            ast.Symbol(('a',)))),)))),)))

    def test_parser_produces_lists_with_literals_on_first_position(self):
        # (1)
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn((1,)),)),)))

        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.List((
                    ast.Int((1,)),)),)))
