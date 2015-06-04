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

from whispy_lispy import skip_steps, scopes2, types


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
    @mock.patch('sys.stdin', StringIO.StringIO('2'))
    @mock.patch('sys.stdout')
    def test_user_input_sum_subtract_return_and_print_in_normal_scope(
            self, stdout_mock):

        scope = scopes2.Scope()
        result = skip_steps.interpret_text2(SAMPLE_SUBTRACT_AND_SUM, scope)

        # Got the user input, calculated stuff, returned a value
        self.assertEqual(result, types.Int((21,)))
        # Printed the result to standard output
        stdout_mock.assert_has_calls([mock.call.write(str(types.Int((7,))))])
