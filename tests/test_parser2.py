# -*- coding utf-8 -*-
from __future__ import unicode_literals

import unittest

from whispy_lispy import parser2, cst, ast, keywords, types

i = cst.IncrementNesting
d = cst.DecrementNesting
cn = cst.ConcreteSyntaxNode
an = ast.AbstractSyntaxNode

class Parser2TestCase(unittest.TestCase):
    def test_simple_list_is_created(self):
        # (a)
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
        # 'a
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((cn(('\'',)), cn(('a',)))))

        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.List((ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
                          ast.Symbol(('a',)))),)))

    def test_transform_2_non_nested_quote_operators_into_function_calls(self):
        # 'a 1 'b
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
                ast.List((
                    ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
                    ast.Symbol(('a',)))),
                ast.Value((types.Int((1,)),)),
                ast.List((
                    ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
                    ast.Symbol(('b',)))),
            )))

    def transform_3_nested_quote_operators_into_function_calls(self):
        # '''a
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn(('\'',)), cn(('\'',)), cn(('\'',)), cn(('a',))
            )))
        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.List((
                    ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
                    ast.List((
                        ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
                        ast.List((
                            ast.Symbol((keywords.BUILTIN_QUOTE_FUNC,)),
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
                    ast.Value((types.Int((1,)),)),)),)))

    def test_all_literal_types_are_created(self):
        # 1 2.3 "x" #t
        result = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((1,)), cn((2.3,)), cn(('"x"',)), cn((True,)),)))

        self.assertEqual(
            result,
            ast.RootAbstractSyntaxNode((
                ast.Value((types.Int((1, )),)),
                ast.Value((types.Float((2.3,)),)),
                ast.Value((types.String(('x',)),)),
                ast.Value((types.Bool((True,)),))
            ))
        )

    def test_nested_list_with_literal_types(self):
        # ("x" 1 (#t 3.14))
        actual = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn(('"x"',)),
                    cn((1,)),
                    cn((
                        cn((True,)),
                        cn((3.14,)))))),)))
        expected = ast.RootAbstractSyntaxNode((
            ast.List((
                ast.Value((types.String(('x',)),)),
                ast.Value((types.Int((1,)),)),
                ast.List((
                    ast.Value((types.Bool((True,)),)),
                    ast.Value((types.Float((3.14,)),)))))),))

        self.assertEqual(actual, expected)


class ParserAssignmentTestCase(unittest.TestCase):
    def test_simple_variable_assignment(self):
        # (def x 1)
        actual = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn((keywords.DEFINITION,)),  # def
                    cn(('x',)),
                    cn((14,)))),)))
        expected = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)),
                ast.Value((types.Int((14,)),))
            )),
        ))
        self.assertEqual(actual, expected)

    def test_nested_variable_assignment(self):
        # (def x (def y 33)) - could happen...
        actual = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn((keywords.DEFINITION,)),
                    cn(('x',)),
                    cn((
                        cn((keywords.DEFINITION,)),
                        cn(('y',)),
                        cn((33,)))))),)))
        expected = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)),
                ast.Assign((
                    ast.Symbol(('y',)),
                    ast.Value((types.Int((33,)),)))))),))
        self.assertEqual(actual, expected)

    def test_simple_function_definition_syntax(self):
        # (def (f) 1)
        actual = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn((keywords.DEFINITION,)),
                    cn((
                        cn(('f',)),)),
                    cn((1,)))),)))
        expected = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),)),
                ast.Value((types.Int((1,)),)))),))
        self.assertEqual(actual, expected)

    def test_nested_function_and_variable_assignment(self):
        # (def (f (def y 9)) (def z (def (t g v) 87)))
        actual = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn((keywords.DEFINITION,)),
                    cn((
                        cn(('f',)),
                        cn((
                            cn((keywords.DEFINITION,)),
                            cn(('y',)),
                            cn((9,)))))),
                    cn((
                        cn((keywords.DEFINITION,)),
                        cn(('z',)),
                        cn((
                            cn((keywords.DEFINITION,)),
                            cn((
                                cn(('t',)),
                                cn(('g',)),
                                cn(('v',)))),
                            cn((87,)))))))),)))
        expected = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Assign((             # This won't get evaluated
                        ast.Symbol(('y',)),
                        ast.Value((types.Int((9,)),)))))),
                ast.Assign((
                    ast.Symbol(('z',)),
                    ast.Assign((
                        ast.List((
                            ast.Symbol(('t',)),
                            ast.Symbol(('g',)),
                            ast.Symbol(('v',)))),
                        ast.Value((types.Int((87,)),)))),)))),))
        self.assertEqual(actual, expected)


class ConditionTestCase(unittest.TestCase):
    def test_nested_condition_with_every_alias_is_parsed(self):
        # (cond (#f 1) (#t (if (#f 2))))
        actual = parser2.get_ast_from_cst(
            cst.RootConcreteSyntaxnode((
                cn((
                    cn(('cond',)),
                    cn((
                        cn((False,)),
                        cn((1,)))),
                    cn((
                        cn((True,)),
                        cn((
                            cn(('if',)),
                            cn((
                                cn((False,)),
                                cn((2,)))))))))),)))
        expected = ast.RootAbstractSyntaxNode((
            ast.Condition((
                ast.List((
                    ast.Value((types.Bool((False,)),)),
                    ast.Value((types.Int((1,)),)))),
                ast.List((
                    ast.Value((types.Bool((True,)),)),
                    ast.Condition((
                        ast.List((
                            ast.Value((types.Bool((False,)),)),
                            ast.Value((types.Int((2,)),)))),)))))),))
        self.assertEqual(actual, expected)
