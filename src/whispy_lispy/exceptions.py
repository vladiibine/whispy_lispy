# -*- coding utf-8 -*-
"""Defines the internal base exceptions for whispy lispy"""
from __future__ import unicode_literals


class BaseWhispyLispyError(Exception):
    pass


class WhispyLispySyntaxError(BaseWhispyLispyError):
    def __init__(self, source, index, extra_info):
        """
        :param str source: the source code that contains the error
        :param int index: the source index where the error begins
        """
        line, row, indication = self.get_all_template_params(source, index)
        msg = (
            "\nSyntax error at line {line}, row {row}:\n{extra}\n"
            "\n{indication}\n\n"  # noqa
            .format(line=line, row=row, indication=indication, extra=extra_info
            ))
        super(WhispyLispySyntaxError, self).__init__(msg)

    @classmethod
    def get_all_template_params(cls, source, index):
        last_newline_index = cls.get_last_newline_index(source, index)
        row = cls.get_error_row(index, last_newline_index)
        line = cls.get_error_line(source, index)
        indication = cls.get_error_indication(source, index, row)  # noqa
        return line, row, indication

    @staticmethod
    def get_last_newline_index(source, index):
        return source.rfind('\n', 0, index) if source else 0

    @staticmethod
    def get_error_line(source, index):
        return source.count('\n', 0, index) + 1 if source else None

    @staticmethod
    def get_error_row(index, last_newline_index):
        return (index or 0) - last_newline_index

    @staticmethod
    def get_error_indication(source, index, row):
        """Get the line number, and a portion of the source surrounding the
        error

        :param str source: the entire source code
        :param int index: the code section from the error until the end
        :param int row: the row where the error occurred
        :rtype: str
        """
        if index is None or source is None:
            return

        above = '\n'.join(source[:index].split('\n')[-3:])
        the_line = '\n'.join(source[index:].split('\n')[:1])
        error_indication = (
            ' ^ '.rjust(row) + 'This is where the error occurred'
        )

        displayable_source = '\n'.join((above + the_line, error_indication))
        return displayable_source


class UnboundSymbol(BaseWhispyLispyError):
    pass


class EvaluationError(BaseWhispyLispyError):
    pass
