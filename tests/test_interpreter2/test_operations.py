# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from tests.constructors import *
from whispy_lispy import interpreter2, exceptions


class OperatorsTestCase(unittest.TestCase):
    def test_operator_equal_unary(self):
        # (= 9)
        tree = a_r(
            a_li(
                a_o('='),
                a_v(9)))
        self.assertEqual(interpreter2.interpret_ast(tree), t_b(True))

    def test_operator_equal_multi_params(self):
        # (= 1 1 1 1 1)
        tree = a_r(
            a_li(
                a_o('='),
                a_v(1), a_v(1), a_v(1), a_v(1), a_v(1),))
        self.assertEqual(interpreter2.interpret_ast(tree), t_b(True))

    def test_operator_plus_unary(self):
        # (+ 1.4)
        tree = a_r(
            a_li(
                a_o('+'),
                a_v(1.4)))

        self.assertEqual(interpreter2.interpret_ast(tree), t_f(1.4))

    def test_operator_plus_multi_params(self):
        # (+ 1 2 3)
        tree = a_r(
            a_li(
                a_o('+'),
                a_v(1), a_v(2), a_v(3)))
        self.assertEqual(interpreter2.interpret_ast(tree), t_i(6))

    def test_operator_plus_different_compatible_param_types(self):
        # (+ 1 2.2)
        tree = a_r(
            a_li(
                a_o('+'),
                a_v(1), a_v(2.2)))
        self.assertEqual(interpreter2.interpret_ast(tree), t_f(3.2))

    def test_operator_plus_different_incompatible_param_types(self):
        # (+ 1 #t)
        tree = a_r(
            a_li(
                a_o('+'),
                a_v(1), a_v(True)))
        self.assertRaises(
            exceptions.EvaluationError,
            interpreter2.interpret_ast,
            tree)

    def test_operator_plus_with_bools(self):
        # (+ #t #f)
        tree = a_r(
            a_li(
                a_o('+'),
                a_v(True), a_v(False)))

        result = interpreter2.interpret_ast(tree)
        self.assertEqual(result, t_b(True))

    def test_operator_plus_with_strings(self):
        # (+ "a" "b")
        tree = a_r(
            a_li(
                a_o('+'),
                a_v("a"), a_v("b")))
        self.assertEqual(interpreter2.interpret_ast(tree), t_str("ab"))
