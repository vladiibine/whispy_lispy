# coding -*- utf-8 -*-
"""Defines some convenience functions that chain some steps from the lexical
analysis of the text, building the abstract syntax tree and interpreting this
tree
"""
from __future__ import unicode_literals

from whispy_lispy import parser, lexer, interpreter, scopes


def get_ast_from_text(text):
    """Return the abstract syntax tree for this source text

    :param str|unicode text: a text to be parsed into an Abstract syntax tree
    """
    return parser.get_ast2(lexer.get_concrete_syntax_tree(
        lexer.get_flat_token_list(text)
    ))


def interpret_text(text):
    """Run all the steps from parsing the text to interpreting it
    :param str|unicode text: the source text
    """
    return interpreter.interpret_ast(get_ast_from_text(text), scopes.Scope())
