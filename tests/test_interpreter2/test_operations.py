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
        # Adds all types together. All inter-type additions should fail,
        # except for the int-float combination
        def generate_tree(t1, t2):
            return a_r(
                a_li(
                    a_o('+'),
                    a_v(t1), a_v(t2)))

        elem_types = [1, 2.2, True, "a"]
        failed_to_raise = []
        for type1 in elem_types:
            for type2 in elem_types:
                if (type1 is not type2
                        and not {type(type1), type(type2)} == {int, float}):
                    try:
                        interpreter2.interpret_ast(generate_tree(type1, type2))
                    except exceptions.EvaluationError:
                        pass
                    else:
                        failed_to_raise.append((type1, type2))
        if failed_to_raise:
            self.fail("Failed to raise EvaluationError for : {}"
                      .format(failed_to_raise))

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
