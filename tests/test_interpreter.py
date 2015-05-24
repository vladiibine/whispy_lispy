# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest

from whispy_lispy import interpreter, ast, exceptions


class InterpreterTest(unittest.TestCase):
    def test_interpret_empty_ast(self):
        self.assertEqual(interpreter.interpret([]), None)

    def test_interpret_int(self):
        self.assertEqual(interpreter.interpret([3]), 3)

    def test_interpret_return_last_value(self):
        self.assertEqual(interpreter.interpret([3, 4, 5]), 5)

    def test_assignment_changes_global_scope(self):
        scope = {}
        interpreter.interpret([ast.Assign('x', 3)], scope)
        self.assertEqual(scope['x'], 3)

    def test_assignment_returns_nothing(self):
        scope = {}
        result = interpreter.interpret([ast.Assign('x', 3)], scope)
        self.assertIsNone(result)

    def test_assignments_change_scope_and_interpreter_returns_value(self):
        scope = {}
        result = interpreter.interpret([ast.Assign('x', 6), 4], scope)
        self.assertEqual(scope['x'], 6)
        self.assertEqual(result, 4)

    def test_assignment_from_another_assigned_symbol(self):
        scope = {}
        interpreter.interpret([ast.Assign('x', 6), ast.Assign('y', 'x')], scope)  # noqa
        self.assertEqual(scope['y'], 6)

    def test_assignment_from_missing_symbol(self):
        scope = {}
        self.assertRaises(
            exceptions.LispyUnboundSymbolError,
            interpreter.interpret,
            [ast.Assign('x', 'y')], scope
        )
