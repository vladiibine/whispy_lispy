# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from tests.constructors import a_r, a_c, a_li, a_v, a_s
from whispy_lispy import ast, types, interpreter2, scopes2


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