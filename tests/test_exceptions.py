# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from whispy_lispy import exceptions


class SyntaxErrorTestCase(unittest.TestCase):
    def test_error_on_first_line(self):
        text = """(fff...)"""
        index = text.index('.')

        syntax_err = exceptions.WhispyLispySyntaxError(text, index, None)

        line, row, _ = syntax_err.get_all_template_params(text, index)

        self.assertEqual(line, 1)
        self.assertEqual(row, index + 1)

    def test_error_on_line_in_middle(self):
        text = "(\nff\n\n  gg...)"
        index = text.index('.')

        syntax_err = exceptions.WhispyLispySyntaxError(text, index, None)

        line, row, _ = syntax_err.get_all_template_params(text, index)

        self.assertEqual(line, 4)
        self.assertEqual(row, 5)
