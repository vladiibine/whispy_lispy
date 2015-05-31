# -*- coding utf-8 -*-
"""Integration-ish tests
"""
from __future__ import absolute_import, unicode_literals

import unittest
import six

if six.PY2:
    import StringIO
    import mock
else:
    from unittest import mock
    import io as StringIO

from whispy_lispy import interpreter, skip_steps


SAMPLE_SUM_NUMBERS_AND_RETURN_VALUE = """\
(def a 3)
(def b 4)
(def x (sum a b))
8
"""

SAMPLE_SUBTRACT_AND_SUM = """\
(def user_input (simple_input))
(def x (sum 1 (sub 9 (sum 1 user_input))))
(print x)
(sum x 14)
"""


class IntegrationTestCase(unittest.TestCase):
    def test_sum_3_numbers_in_dummy_scope(self):
        scope = {'sum': lambda *nums: sum(nums)}
        ast = skip_steps.get_ast_from_text(SAMPLE_SUM_NUMBERS_AND_RETURN_VALUE)
        result = interpreter.interpret_ast(ast, scope)

        self.assertEqual(scope['x'], 7)
        self.assertEqual(result, 8)

    @mock.patch('sys.stdin', StringIO.StringIO('2'))
    @mock.patch('sys.stdout')
    def test_user_input_sum_subtract_return_and_print_in_normal_scope(
            self, stdout_mock):
        result = skip_steps.interpret_text(SAMPLE_SUBTRACT_AND_SUM)

        # Got the user input, calculated stuff, returned a value
        self.assertEqual(result, 21)
        # Printed the result to standard output
        stdout_mock.assert_has_calls([mock.call.write('7')])
