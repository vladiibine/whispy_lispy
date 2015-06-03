# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import
import unittest

from whispy_lispy import parser2, ast, types


class NativeTypeConversion(unittest.TestCase):
    def test_return_int(self):
        result = parser2.get_native_types_from_ast(
            ast.RootAbstractSyntaxNode((
                ast.Int((1,)),)))

        self.assertEqual(
            result,
            (types.Int((1,)),)
        )

    def test_return_all_simple_types(self):
        result = parser2.get_native_types_from_ast(
            ast.RootAbstractSyntaxNode((
                ast.Int((8,)),
                ast.String(('a',)),
                ast.Bool((True,)),
                ast.Float((3.14,)))))

        self.assertEqual(
            result,
            (
                types.Int((8,)),
                types.String(('a',)),
                types.Bool((True,)),
                types.Float((3.14,))
            )
        )

    def test_return_native_list(self):
        result = parser2.get_native_types_from_ast(
            ast.RootAbstractSyntaxNode((
                ast.List((
                    ast.Symbol(('a',)),)),)))

        self.assertEqual(
            result, (
                types.List((
                    types.Symbol(('a',)),
                )),))
