# -*- coding utf-8 -*-
from __future__ import unicode_literals
import unittest

from whispy_lispy import parser, ast, cst


def cn(val):
    """Return a ConcreteSyntaxNode """
    return create_any_node(val, cst.ConcreteSyntaxNode)

def rcn(val):
    """Return the root ConcreteSyntaxNode"""
    return create_any_node(val, cst.RootConcreteSyntaxnode)


def create_any_node(val, node_cls):
    if isinstance(val, tuple):
        return node_cls(val)
    else:
        return node_cls((val,))

def an(val):
    """Return an AbstractSyntaxNode """
    return create_any_node(val, ast.AbstractSyntaxNode)

def ran(val):
    """Return the root AbstractSyntaxNode"""
    return create_any_node(val, ast.RootAbstractSyntaxNode)


class ParserOutputStructureTestCase(unittest.TestCase):
    def _to_chained_list(self, node):
        if node.is_leaf():
            return node.values

        result = []
        for elem in node.values:
            result.append(self._to_chained_list(elem))

        return result

    def assertNodeStructureEqual(self, n1, n2, msg=None):
        """Used to for comparing node structure only (node types might differ)
        """
        self.assertEqual(
            self._to_chained_list(n1), self._to_chained_list(n2), msg)

    def test_parses_empty_root_node(self):
        self.assertEqual(
            parser.get_ast2(rcn(())), ran(()))

    def test_root_csnode_is_not_nonroot_asnode(self):
        self.assertNotEqual(parser.get_ast2(rcn(())), an(()))

    def test_nonroot_csnode_is_not_root_asnode(self):
        self.assertNotEqual(parser.get_ast2(cn(())), ran(()))

    def test_parses_empty_non_root_node(self):
        self.assertNodeStructureEqual(
            parser.get_ast2(cn(())), an(()))

    def test_parses_non_empty_non_root(self):
        self.assertNodeStructureEqual(parser.get_ast2(cn(2)), an(2))

    def test_parses_single_element(self):
        self.assertNodeStructureEqual(
            parser.get_ast2(cn(cn(1))), an(an(1)))

    def test_parse_simple_nested_structure(self):
        self.assertNodeStructureEqual(
            parser.get_ast2(cn((cn('a'), cn(2)))),
            an((an('a'), an(2))))

    def test_parse_more_nested_structure(self):
        actual = parser.get_ast2(
            rcn((cn(1), cn((cn(2), cn((cn(3), cn(4), cn(5))))), cn(6))))
        expected = ran((an(1), an((an(2), an((an(3), an(4), an(5))))), an(6)))

        self.assertNodeStructureEqual(actual, expected)


class ParserOperationsTestCase(unittest.TestCase):
    def test_simple_apply(self):
        result_ast = parser.get_ast2(rcn(cn((cn('a'), cn(2)))))

        self.assertIsInstance(result_ast[0], ast.Apply)

    def test_nested_apply(self):
        result_ast = parser.get_ast2(
            rcn(cn((cn('a'), cn('b'), cn((cn('c'), cn(1)))))))

        self.assertIsInstance(result_ast[0], ast.Apply)
        self.assertIsInstance(result_ast[0][2], ast.Apply)

    def test_apply_quote_to_symbol(self):
        result_ast = parser.get_ast2(rcn(cn((cn('quote'), cn('a')))))

        self.assertIsInstance(result_ast[0], ast.Quote)
        self.assertTrue(len(result_ast[0].values), 1)

    def test_apply_quote_and_symbol(self):
        result_ast = parser.get_ast2(rcn((cn((cn('a'), cn('quote'), cn('b'))))))  # noqa

        self.assertIsInstance(result_ast[0], ast.Apply)
        self.assertIsInstance(result_ast[0][0], ast.AbstractSyntaxNode)  # noqa
        self.assertIsInstance(result_ast[0][1], ast.Quote)

    def test_quote_children_are_not_evaluable(self):
        result_ast = parser.get_ast2(
            rcn((
                cn('a'),
                cn((
                    cn('list'),
                    cn(1),
                    cn((
                        cn('quote'),
                        cn('a'),
                        cn('b'),
                        cn((
                            cn('sum'),
                            cn(1),
                            cn(2)
                        )))),
                    cn('c'))))))

        self.assertTrue(result_ast.is_evaluable())
        self.assertTrue(result_ast[0].is_evaluable())  # The root
        self.assertTrue(result_ast[1].is_evaluable())  # The 1st apply
        self.assertTrue(result_ast[1][0].is_evaluable())  # The list func
        self.assertTrue(result_ast[1][1].is_evaluable())  # The literal 1
        self.assertTrue(result_ast[1][2].is_evaluable())  # The quote itself
        self.assertTrue(result_ast[1][3].is_evaluable())  # The symbol 'c'

        self.assertFalse(result_ast[1][2][0].is_evaluable())  # the symbol 'a'
        self.assertFalse(result_ast[1][2][1].is_evaluable())  # the symbol 'b'
        self.assertFalse(result_ast[1][2][2].is_evaluable())  # the 2nd apply
        self.assertFalse(result_ast[1][2][2][0].is_evaluable())  # the 'sum'
        self.assertFalse(result_ast[1][2][2][1].is_evaluable())  # literal 1
        self.assertFalse(result_ast[1][2][2][1].is_evaluable())  # literal 2


class ParserTransformationsTestCase(unittest.TestCase):
    def test_simple_quote_operator_to_function(self):
        result_ast = parser.transform_quote_operator_into_function(
            an((ast.OperatorQuote(()), an('a'))))

        self.assertIsInstance(result_ast[0], ast.Apply)
        self.assertIsInstance(result_ast[0][0], ast.Quote)

    def test_nested_quote_operator_to_function(self):
        result_ast = parser.transform_quote_operator_into_function(
            an((ast.OperatorQuote(()), an((an('a'), ast.OperatorQuote(()), an('b')))))  # noqa
        )
        self.assertIsInstance(result_ast[0], ast.Apply)
        self.assertIsInstance(result_ast[0][0], ast.Quote)

        self.assertIsInstance(result_ast[0][0][0][1], ast.Apply)
        self.assertIsInstance(result_ast[0][0][0][1][0], ast.Quote)


class ParserSymbolTestCase(unittest.TestCase):
    def test_simple_symbol(self):
        result_ast = parser.get_ast2(cn('a'))
        self.assertIsInstance(result_ast, ast.Symbol)

    def test_nested_symbols(self):
        result_ast = parser.get_ast2(cn((cn('a'), cn((cn('b'), cn('c'))))))

        self.assertIsInstance(result_ast[0], ast.Symbol)
        self.assertIsInstance(result_ast[1][0], ast.Symbol)
        self.assertIsInstance(result_ast[1][1], ast.Symbol)


class ParserBaseAtomTypesTestCase(unittest.TestCase):
    def test_parse_int_float_bool_simple(self):
        result_ast = parser.get_ast2(cn((cn(1), cn(9.3), cn(True))))

        self.assertIsInstance(result_ast[0], ast.Int)
        self.assertIsInstance(result_ast[1], ast.Float)
        self.assertIsInstance(result_ast[2], ast.Bool)

    def test_mixed_order_multiple_int_float_and_bool(self):
        result_ast = parser.get_ast2(
            cn((cn(True), cn(9.3), cn(True), cn(1), cn(True), cn(False),
                cn(8.3), cn(2), cn(4), cn(1.2)))
        )
        self.assertIsInstance(result_ast[0], ast.Bool)
        self.assertIsInstance(result_ast[1], ast.Float)
        self.assertIsInstance(result_ast[2], ast.Bool)
        self.assertIsInstance(result_ast[3], ast.Int)
        self.assertIsInstance(result_ast[4], ast.Bool)
        self.assertIsInstance(result_ast[5], ast.Bool)
        self.assertIsInstance(result_ast[6], ast.Float)
        self.assertIsInstance(result_ast[7], ast.Int)
        self.assertIsInstance(result_ast[8], ast.Int)
        self.assertIsInstance(result_ast[9], ast.Float)


class AssignmentTestCase(unittest.TestCase):
    def test_simple_assignment(self):
        # (def x 9)
        result_ast = parser.get_ast2(cn((cn('def'), cn('x'), cn(9))))

        self.assertEqual(len(result_ast.values), 2)
        self.assertIsInstance(result_ast, ast.Assign)
        self.assertIsInstance(result_ast[0], ast.Symbol)

    def test_nested_assignments(self):
        # (def x (list (def y 1) 2))
        result_ast = parser.get_ast2(
            cn((
                cn('def'),
                cn('x'),
                cn((
                    cn('list'),
                    cn((
                        cn('def'), cn('y'), cn(1))),
                    cn(2))))))

        self.assertIsInstance(result_ast, ast.Assign)
        self.assertIsInstance(result_ast[1][1], ast.Assign)

class CarTestCase(unittest.TestCase):
    def test_simple_car_function(self):
        result_ast = parser.get_ast2(cn((cn('car'), cn((cn('list'), cn(1))))))

        self.assertIsInstance(result_ast, ast.First)
        self.assertIsInstance(result_ast[0], ast.Apply)
        self.assertEqual(len(result_ast[0].values), 2)

    def test_nested_car_function_calls(self):
        result_ast = parser.get_ast2(
            cn((cn('car'), cn((cn('list'), cn((cn('car'), cn('x'))))))))

        self.assertIsInstance(result_ast, ast.First)
        self.assertIsInstance(result_ast[0][1], ast.First)
