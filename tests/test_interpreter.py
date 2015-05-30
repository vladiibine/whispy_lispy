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
