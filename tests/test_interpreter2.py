# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest
from whispy_lispy import interpreter2, ast, types, scopes2


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
        # (def (f) 1)
        # function that returns a constant
        tree = ast.RootAbstractSyntaxNode((
            ast.Assign((
                ast.List((ast.Symbol(('f',)),)),
                ast.Value((types.Int((45,)),)))),))
        scope = scopes2.Scope()
        interpreter2.interpret_ast(tree, scope)
        self.assertEqual(
            scope[types.Symbol(('f',))],
            types.Function((
                types.String(('f',)),
                (),
                ast.Value((types.Int((45,)),)))))

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
                ast.Value((types.Int((16,)),)),)))


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
