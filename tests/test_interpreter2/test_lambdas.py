# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from tests.constructors import a_r, a_la, a_li, a_v, a_s, t_s, a_a
from whispy_lispy import interpreter2, types, scopes2


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