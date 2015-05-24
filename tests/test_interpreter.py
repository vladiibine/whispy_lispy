# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest

from whispy_lispy import interpreter, ast, exceptions


class ReturnValueTestCase(unittest.TestCase):
    def test_interpret_empty_ast(self):
        self.assertEqual(interpreter.interpret([]), None)

    def test_interpret_int(self):
        self.assertEqual(interpreter.interpret([ast.Literal(3)]), 3)

    def test_interpret_return_last_value(self):
        self.assertEqual(interpreter.interpret([ast.Literal(3),
                                                ast.Literal(4),
                                                ast.Literal(5)]),
                         5)


class AssignTestCase(unittest.TestCase):
    def test_assignment_changes_global_scope(self):
        scope = {}
        interpreter.interpret([ast.Assign(ast.Symbol('x'), ast.Literal(3))], scope)  # noqa
        self.assertEqual(scope['x'], 3)

    def test_assignment_returns_nothing(self):
        scope = {}
        result = interpreter.interpret([ast.Assign('x', 3)], scope)
        self.assertIsNone(result)

    def test_assignments_change_scope_and_interpreter_returns_value(self):
        scope = {}
        result = interpreter.interpret(
            [
                ast.Assign(
                    ast.Symbol('x'),
                    ast.Literal(6)),
                ast.Literal(4)
            ], scope)
        self.assertEqual(scope['x'], 6)
        self.assertEqual(result, 4)

    def test_assignment_from_another_assigned_symbol(self):
        scope = {}
        interpreter.interpret(
            [ast.Assign(ast.Symbol('x'), ast.Literal(6)),
             ast.Assign(ast.Symbol('y'), ast.Symbol('x'))], scope)
        self.assertEqual(scope['y'], 6)

    def test_assignment_from_missing_symbol(self):
        scope = {}
        self.assertRaises(
            exceptions.LispyUnboundSymbolError,
            interpreter.interpret,
            [ast.Assign(ast.Symbol('x'), ast.Symbol('y'))], scope
        )

class ApplyTestCase(unittest.TestCase):
    def test_sum_numbers(self):
        def native_sum_mock(scope, args):
            return sum([arg.eval(scope) for arg in args])

        scope = {'sum': native_sum_mock}
        result = interpreter.interpret(
            [ast.Apply(ast.Symbol('sum'), ast.Literal(9), ast.Literal(8))], scope)  # noqa

        self.assertEqual(result, 17)

    def test_missing_function(self):
        self.assertRaises(
            exceptions.LispyUnboundSymbolError,
            interpreter.interpret,
            [ast.Apply(ast.Symbol('sum'), ast.Literal(9), ast.Literal(8))]
        )

class EvalQuoteTestCase(unittest.TestCase):
    def test_quote_sum(self):
        def native_sum_mock(scope, args):
            return sum(args)
        scope = {'sum': native_sum_mock}
        self.assertEqual(
            interpreter.interpret(
                [ast.Eval(ast.Quote([ast.Apply([
                    ast.Symbol('sum'),
                    ast.Literal(1),
                    ast.Literal(2)])]))],
                scope),  # noqa
            1
        )
