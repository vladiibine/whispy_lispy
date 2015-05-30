# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest

from whispy_lispy import interpreter, ast

class InterpreterTestCase(unittest.TestCase):
    def test_return_the_only_provided_value(self):
        tree = ast.RootAbstractSyntaxNode((ast.Int((3,)),))

        self.assertEqual(interpreter.interpret_ast(tree, {}), 3)

    def test_return_the_last_provided_value(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Int((3,)), ast.Float((3.3,)), ast.Bool((True,))
        ))

        self.assertEqual(interpreter.interpret_ast(tree, {}), True)

    def test_simple_literal_assignment_and_returns_nothing(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((ast.Symbol(('x',)), ast.Int((3,)))),
        ))

        scope = {}
        result = interpreter.interpret_ast(tree, scope)

        self.assertEqual(result, None)
        self.assertEqual(scope['x'], 3)

    def test_symbol_assignment(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)), ast.Symbol(('y',))
            )),
        ))
        scope = {'y': 3}

        interpreter.interpret_ast(tree, scope)

        self.assertEqual(scope['x'], 3)

    def test_symbol_assignment_from_literal_assignment(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((ast.Symbol(('x',)), ast.Int((3,)))),
            ast.Assign((ast.Symbol(('y',)), ast.Symbol(('x',))))
        ))

        scope = {}
        interpreter.interpret_ast(tree, scope)
        self.assertEqual(scope['y'], 3)

    def test_simple_sum_apply(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Apply((ast.Symbol(('sum',)), ast.Int((3,)), ast.Int((4,)))),
        ))

        # Mock a native sum function
        scope = {'sum': lambda *nums: sum(value[0] for value in nums)}

        result = interpreter.interpret_ast(tree, scope)

        self.assertEqual(result, 7)

    def test_assign_value_of_apply_sum(self):
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.Symbol(('x',)),
                ast.Apply((
                    ast.Symbol(('sum',)),
                    ast.Int((3,)),
                    ast.Int((2,)))))),))

        # Mock a native sum function
        scope = {'sum': lambda *nums: sum(value[0] for value in nums)}

        result = interpreter.interpret_ast(tree, scope)
        self.assertEqual(result, None)
        self.assertEqual(scope['x'], 5)
