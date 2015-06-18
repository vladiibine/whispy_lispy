# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from whispy_lispy import ast, types, scopes2, interpreter2
from ..constructors import *


class FunctionCreationTestCase(unittest.TestCase):
    def test_simple_function_returning_constant_is_created(self):
        # (def (f) 45)
        # function that returns a constant
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((ast.Symbol(('f',)),)),
                ast.Value((types.Int((45,)),)))),))
        scope = scopes2.Scope()
        interpreter2.interpret_ast(tree, scope)

        new_function = types.Function((
            types.String(('f',)), (),
            ast.Value((types.Int((45,)),)),
            scope,))
        self.assertEqual(scope[types.Symbol(('f',))], new_function)

    def test_simple_function_with_parameters_is_created(self):
        # (def (f a b) 16
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',))
                )),
                ast.Value((types.Int((16,)),)))),))
        scope = scopes2.Scope()
        interpreter2.interpret_ast(tree, scope)
        self.assertEqual(
            scope[types.Symbol(('f',))],
            types.Function((
                types.String(('f',)),
                (types.Symbol(('a',)), types.Symbol(('b',))),
                ast.Value((types.Int((16,)),)),
                scope)))


class FunctionExecutionTestCase(unittest.TestCase):
    def test_simple_function_returns_constant_value(self):
        # (def (f) 1)
        # (f)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),)),
                ast.Value((types.Int((1,)),)))),
            ast.List((ast.Symbol(('f',)),))
        ))
        result = interpreter2.interpret_ast(tree)

        self.assertEqual(result, types.Int((1,)))

    def test_simple_function_wraps_sum(self):
        # (def (f a b) (sum a b))
        # (f 11 22)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',))
                )),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)),)))),
            ast.List((
                ast.Symbol(('f',)),
                ast.Value((types.Int((11,)),)),
                ast.Value((types.Int((22,)),))
            ))
        ))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((33,)))

    def test_function_calls_another_function(self):
        # (def (f a b) (sum a b 3))
        # (def (g x y) (sum (f x y) 4))
        # (g 10 20)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)),)),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)),
                    ast.Value((types.Int((3,)),)))),)),
            ast.Assign((
                ast.List((
                    ast.Symbol(('g',)),
                    ast.Symbol(('x',)),
                    ast.Symbol(('y',)),)),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.List((
                        ast.Symbol(('f',)),
                        ast.Symbol(('x',)),
                        ast.Symbol(('y',)),)),
                    ast.Value((types.Int((4,)),)))))),
            ast.List((
                ast.Symbol(('g',)),
                ast.Value((types.Int((10,)),)),
                ast.Value((types.Int((20,)),))))))

        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((37,)))

    def test_function_passes_arguments_to_another_function(self):
        # (def (f a) (sum 1 a))
        # (def (g b) (sum (f b) 3))
        # (g 5)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('a',)))),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.Value((types.Int((1,)),)),
                    ast.Symbol(('a',)))))),
            ast.Assign((
                ast.List((
                    ast.Symbol(('g',)),
                    ast.Symbol(('b',)))),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.List((
                        ast.Symbol(('f',)),
                        ast.Symbol(('b',)))),
                    ast.Value((types.Int((3,)),)))))),
            ast.List((
                ast.Symbol(('g',)),
                ast.Value((types.Int((5,)),))))))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((9,)))

    def test_passing_arguments_with_the_same_name(self):
        # (def (f a b) (sum a b))
        # (def (g a b) (f a b))
        # (g 1 2)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)))),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)))))),
            ast.Assign((
                ast.List((
                    ast.Symbol(('g',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)))),
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('a',)),
                    ast.Symbol(('b',)))))),
            ast.List((
                ast.Symbol(('g',)),
                ast.Value((types.Int((1,)),)),
                ast.Value((types.Int((2,)),)),
            ))))

        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((3,)))

    def test_unconditional_recursion(self):
        # Test methods (i.e. those named 'test_*' are treated differently
        # by nose. So differently, that some runtime errors
        # (like when too many recursions happen) can't get asserts on them
        self.assertRaises(
            RuntimeError,
            self._test_unconditional_recursion_helper_because_pytest_sux,
            )

    def _test_unconditional_recursion_helper_because_pytest_sux(self):
        # Not stackless yet, so raise error for infinite recursion
        # (def (f x) (f x))
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('x',)),)),
                ast.List((
                    ast.Symbol(('f',)),
                    ast.Symbol(('x',)),)))),
            ast.List((
                ast.Symbol(('f',)),
                ast.Value((types.Int((3,)),)))),))

        interpreter2.interpret_ast(tree)

    def test_function_returns_function(self):
        # (def (f) 1)
        # (def (g) f)
        # (g)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),)),
                ast.Value((types.Int((1,)),)))),
            ast.Assign((
                ast.List((
                    ast.Symbol(('g',)),)),
                ast.Symbol(('f',)))),
            ast.List((
                ast.Symbol(('g',)),))))

        scope = scopes2.Scope()
        result = interpreter2.interpret_ast(tree, scope)
        self.assertEqual(result, scope[types.Symbol(('f',))])

    def test_dynamic_function_call(self):
        # (def (f) 1)
        # (def (g) f)
        # (def (h) g)
        # (((h)))
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),)),
                ast.Value((types.Int((1,)),)))),
            ast.Assign((
                ast.List((
                    ast.Symbol(('g',)),)),
                ast.Symbol(('f',)))),
            ast.Assign((
                ast.List((
                    ast.Symbol(('h',)),)),
                ast.Symbol(('g',)))),
            ast.List(((
                ast.List((
                    ast.List((
                        ast.Symbol(('h',)),)),)),)))))

        scope = scopes2.Scope()
        result = interpreter2.interpret_ast(tree, scope)

        self.assertEqual(result, types.Int((1,)))

    def test_recursive_evaluation_of_factorial(self):
        # (def (fact n) (cond ((= n 1) 1) (#t (* n (fact (sub n 1)))))))
        # (fact 5)
        tree = a_r(
            a_a(
                a_li(
                    a_s('fact'),
                    a_s('n')),
                a_c(
                    a_li(
                        a_li(
                            a_o('='),
                            a_s('n'),
                            a_v(1)),
                        a_v(1)),
                    a_li(
                        a_v(True),
                        a_li(
                            a_o('*'),
                            a_s('n'),
                            a_li(
                                a_s('fact'),
                                a_li(
                                    a_s('sub'),
                                    a_s('n'),
                                    a_v(1))))))),
            a_li(
                a_s('fact'),
                a_v(5)))

        self.assertEqual(interpreter2.interpret_ast(tree), t_i(120))
