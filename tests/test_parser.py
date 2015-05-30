# -*- coding utf-8 -*-
from __future__ import unicode_literals
import unittest

from whispy_lispy import parser, ast, cst


class ParserTests(unittest.TestCase):
    def test_parser_parses_empty_tree(self):
        self.assertEqual(parser.get_ast([]), [])

    def test_parser_parses_assignment(self):
        self.assertEqual(
            parser.get_ast([['def', 'x', 1]]), [ast.Assign('x', 1)]
        )

    def test_parser_parses_quotation(self):
        self.assertEqual(
            parser.get_ast([["'", 'a']]),
            [ast.Quote([ast.Symbol('a')])])

    def test_parses_explicit_evaluation(self):
        self.assertEqual(
            parser.get_ast([['eval', "'", ['a', 'b']]]),
            [ast.Eval(ast.Quote([ast.Apply(ast.Symbol('a'), ast.Symbol('b'))]))])  # noqa

    def test_parse_implicit_apply(self):
        self.assertEqual(
            parser.get_ast([['asdf', 3, 4]]),
            [ast.Apply(ast.Symbol('asdf'), ast.Literal(3), ast.Literal(4))])

    def test_parse_assigning_from_assigned_value(self):
        self.assertEqual(
            parser.get_ast([['def', 'x', 9], ['def', 'y', 'x']]),
            [ast.Assign('x', 9), ast.Assign('y', 'x')]
        )

    def test_quote_sum(self):
        result = parser.get_ast([["'", ['sum', 1, 2]]])
        self.assertEqual(
            result,
            [ast.Quote(
                [ast.Apply(ast.Symbol('sum'),
                           ast.Literal(1),
                           ast.Literal(2))])
             ]
        )

    def test_parse_eval_quote_sum(self):
        self.assertEqual(
            parser.get_ast([['eval', "'", ['sum', 1, 2]]]),
            [ast.Eval(
                ast.Quote(
                    [ast.Apply(
                        ast.Symbol('sum'),
                        ast.Literal(1),
                        ast.Literal(2))]))]
        )

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

        self.assertIsInstance(result_ast.values[0], ast.Apply2)

    def test_nested_apply(self):
        result_ast = parser.get_ast2(
            rcn(cn((cn('a'), cn('b'), cn((cn('c'), cn(1)))))))

        self.assertIsInstance(result_ast.values[0], ast.Apply2)
        self.assertIsInstance(result_ast.values[0].values[2], ast.Apply2)

    def test_apply_quote_to_symbol(self):
        result_ast = parser.get_ast2(rcn(cn((cn('quote'), cn('a')))))

        self.assertIsInstance(result_ast.values[0], ast.Apply2)
        self.assertIsInstance(result_ast.values[0].values[0], ast.Quote2)
        self.assertTrue(len(result_ast.values[0].values), 2)

    def test_apply_quote_and_symbol(self):
        result_ast = parser.get_ast2(rcn((cn((cn('a'), cn('quote'), cn('b'))))))  # noqa

        self.assertIsInstance(result_ast.values[0], ast.Apply2)
        self.assertIsInstance(result_ast.values[0].values[0], ast.AbstractSyntaxNode)  # noqa
        self.assertIsInstance(result_ast.values[0].values[1], ast.Quote2)


class ParserTransformationsTestCase(unittest.TestCase):
    def test_simple_quote_operator_to_function(self):
        result_ast = parser.transform_quote_operator_into_function(
            an((ast.OperatorQuote(()), an('a'))))

        self.assertIsInstance(result_ast.values[0], ast.Apply2)
        self.assertIsInstance(result_ast.values[0].values[0], ast.Quote2)

    def test_nested_quote_operator_to_function(self):
        result_ast = parser.transform_quote_operator_into_function(
            an((ast.OperatorQuote(()), an((an('a'), ast.OperatorQuote(()), an('b')))))
        )
        self.assertIsInstance(result_ast[0], ast.Apply2)
        self.assertIsInstance(result_ast[0][0], ast.Quote2)

        self.assertIsInstance(result_ast[0][0][0][1], ast.Apply2)
        self.assertIsInstance(result_ast[0][0][0][1][0], ast.Quote2)


class ParserSymbolTestCase(unittest.TestCase):
    def test_simple_symbol(self):
        result_ast = parser.get_ast2(cn('a'))
        self.assertIsInstance(result_ast, ast.Symbol2)

    def test_nested_symbols(self):
        result_ast = parser.get_ast2(cn((cn('a'), cn((cn('b'), cn('c'))))))

        self.assertIsInstance(result_ast[0], ast.Symbol2)
        self.assertIsInstance(result_ast[1][0], ast.Symbol2)
        self.assertIsInstance(result_ast[1][1], ast.Symbol2)

