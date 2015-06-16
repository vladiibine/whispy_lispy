# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest
from whispy_lispy import interpreter2, ast, types, scopes2

from .constructors import (a_c, a_li, a_r, a_s, a_v, a_la, a_a, t_s)


class InterpreterTestCase(unittest.TestCase):
    def test_return_native_int(self):
        tree = ast.RootAbstractSyntaxNode((ast.Value((types.Int((3, )),)),))
        self.assertEqual(interpreter2.interpret_ast(tree, {}), types.Int((3,)))

    def test_return_the_last_provided_value(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Value((types.Int((3,)),)),
            ast.Value((types.String(('ff',)),))))
        self.assertEqual(
            interpreter2.interpret_ast(tree, {}), types.String(('ff',)))

    def test_simple_literal_assignment_and_returns_nothing(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)),
                ast.Value((types.Int((3,)),)))),))
        scope = {}

        result = interpreter2.interpret_ast(tree, scope)

        self.assertEqual(result, None)
        self.assertEqual(scope[types.Symbol(('x',))], types.Int((3,)))

    def test_sum_internal_function(self):
        # (def x (sum 1 2))
        tree = ast.RootAbstractSyntaxNode((
            ast.List((
                ast.Symbol(('sum',)),
                ast.Value((types.Int((3,)),)),
                ast.Value((types.Int((4,)),))
            )),))

        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((7,)))

    def test_assign_value_from_reference(self):
        # (def x 4)
        # (def y (sum x 1 2)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)),
                ast.Value((types.Int((4,)),))
            )),
            ast.Assign((
                ast.Symbol(('y',)),
                ast.List((
                    ast.Symbol(('sum',)),
                    ast.Symbol(('x',)),
                    ast.Value((types.Int((1,)),)),
                    ast.List((types.Int((2,)),))))))))

        scope = scopes2.Scope()
        interpreter2.interpret_ast(tree, scope)
        self.assertEqual(
            scope[types.Symbol(('y',))], types.Int((7,))
        )

    def test_assign_value_from_reference_simple(self):
        # Had troubles with this one after the last test was passing
        # (def x 9)
        # (def y x)
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)),
                ast.Value((types.Int((9,)),))
            )),
            ast.Assign((
                ast.Symbol(('y',)),
                ast.Symbol(('x',))
            ))
        ))

        scope = scopes2.Scope()
        interpreter2.interpret_ast(tree, scope)
        self.assertEqual(
            scope[types.Symbol(('y',))],
            types.Int((9,))
        )


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


class ConditionEvaluationTestCase(unittest.TestCase):
    def test_simple_condition_is_true(self):
        # (cond (#t "yes"))
        tree = ast.RootAbstractSyntaxNode((
            ast.Condition((
                ast.List((
                    ast.Value((types.Bool((True,)),)),
                    ast.Value((types.String(("yes",)),)))),)),))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.String(("yes",)))

    def test_condition_with_false_branch(self):
        # (cond (#f 1)(#t 3.1))
        tree = ast.RootAbstractSyntaxNode((
            ast.Condition((
                ast.List((
                    ast.Value((types.Bool((False,)),)),
                    ast.Value((types.Int((1,)),)),)),
                ast.List((
                    ast.Value((types.Bool((True,)),)),
                    ast.Value((types.Float((3.1,)),)))))),))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Float((3.1,)))

    def test_condition_returns_first_true_branch(self):
        # (cond (#f 1) (#f 2) (#t 3) ($t 4))
        tree = a_r(
            a_c(
                a_li(
                    a_v(False),
                    a_v(1)),
                a_li(
                    a_v(False),
                    a_v(2)),
                a_li(
                    a_v(True),
                    a_v(3),),
                a_li(
                    a_v(True),
                    a_v(4))))
        self.assertEqual(interpreter2.interpret_ast(tree), types.Int((3,)))

    def test_condition_does_not_evaluate_following_true_branches(self):
        # f - will be a function injected into the scope, as a callback
        # (cond (#t 1) (#t (f)))
        class Callback(object):
            called = False

            def callback(self, *args):
                self.called = True
        tree = a_r(
            a_c(
                a_li(
                    a_v(True),
                    a_v(1)),
                a_li(
                    a_v(True),
                    a_li(
                        a_s('f')))))

        scope = scopes2.Scope()
        callback = Callback()
        scope[types.Symbol(('f',))] = callback.callback

        interpreter2.interpret_ast(tree, scope)
        self.assertFalse(callback.called)

    def test_simple_dynamic_condition(self):
        # (def (f) #t)
        # (cond ((f) #f))
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((
                    ast.Symbol(('f',)),)),
                ast.Value((types.Bool((True,)),)))),
            ast.Condition((
                ast.List((
                    ast.List((
                        ast.Symbol(('f',)),)),
                    ast.Value((types.Bool((False,)),)))),))))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Bool((False,)))


class LambdasTestCase(unittest.TestCase):
    def test_simple_lambda_without_parameters_gets_defined(self):
        # (lambda () 1)
        tree = a_r(
            a_la(
                a_li(),
                a_v(1)))

        actual_function = interpreter2.interpret_ast(tree)
        """ :type: types.Function"""
        self.assertEqual(actual_function.code, a_v(1))
        self.assertEqual(actual_function.params, ())
        self.assertEqual(actual_function.name, 'lambda')

    def test_simple_lambda_without_parameters_gets_executed(self):
        # ((lambda () 1))
        tree = a_r(
            a_li(
                a_la(
                    a_li(),
                    a_v(1))))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((1,)))

    def test_simple_lambda_with_parameters_gets_defined(self):
        # (lambda (x y z) 1)
        tree = a_r(
            a_la(
                a_li(
                    a_s('x'),
                    a_s('y'),
                    a_s('z'),),
                a_v(1)))

        actual_function = interpreter2.interpret_ast(tree)
        """ :type: types.Function"""

        self.assertEqual(actual_function.name, 'lambda')
        self.assertEqual(
            actual_function.params, (t_s('x'), t_s('y'), t_s('z')))
        self.assertEqual(actual_function.code, a_v(1))

    def test_simple_lambda_with_parameters_execution(self):
        # ((lambda (a b c) 1))
        tree = a_r(
            a_li(
                a_la(
                    a_li(
                        a_s('a'), a_s('b'), a_s('c')),
                    a_v(1))))
        result = interpreter2.interpret_ast(tree)

        self.assertEqual(result, types.Int((1,)))

    def test_nested_lambdas(self):
        # (
        #   (lambda (a b) (sum a b))
        #   ((lambda (a b c) (sum a b c 1)) 2 4 8)
        #   ((lambda (x a) (sum x a 16)) 32 64))
        tree = a_r(
            a_li(
                a_la(
                    a_li(
                        a_s('a'), a_s('b')),
                    a_li(
                        a_s('sum'), a_s('a', ), a_s('b'))),
                a_li(
                    a_la(
                        a_li(
                            a_s('a'), a_s('b'), a_s('c')),
                        a_li(
                            a_s('sum'), a_s('a'), a_s('b'), a_s('c'), a_v(1),)),  # noqa
                    a_v(2), a_v(4), a_v(8)),
                a_li(
                    a_la(
                        a_li(
                            a_s('x'), a_s('a')),
                        a_li(
                            a_s('sum'), a_s('x'), a_s('a'), a_v(16))),
                    a_v(32), a_v(64))))
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((127,)))

    def test_simple_closure(self):
        # (def (f x) (lambda (y) (sum x y)))
        # ((f 1) 2)
        tree = a_r(
            a_a(
                a_li(
                    a_s('f'),
                    a_s('x'),),
                a_la(
                    a_li(
                        a_s('y')),
                    a_li(
                        a_s('sum'),
                        a_s('x'),
                        a_s('y'),))),
            a_li(
                a_li(
                    a_s('f'),
                    a_v(1)),
                a_v(2)))
        # import pydevd; pydevd.settrace()
        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, types.Int((3,)))

    def test_closures(self):
        # (def (f x) (lambda (y) (sum x y)))
        # (def (f3 z) ((f 3) z))
        # (f3 4)
        tree = a_r(
            a_a(
                a_li(
                    a_s('f'),
                    a_s('x'),),
                a_la(
                    a_li(
                        a_s('y')),
                    a_li(
                        a_s('sum'),
                        a_s('x'),
                        a_s('y'),))),
            a_a(
                a_li(
                    a_s('f3'),
                    a_s('z')),
                a_li(
                    a_li(
                        a_s('f'),
                        a_v(3)),
                    a_s('z'))),
            a_li(
                a_s('f3'),
                a_v(4)))
        scope = scopes2.Scope()

        result = interpreter2.interpret_ast(tree, scope)

        self.assertEqual(result, types.Int((7,)))
