# coding -*- utf-8 -*-
"""Defines some convenience functions that chain some steps from the lexical
analysis of the text, building the abstract syntax tree and interpreting this
tree
"""
from __future__ import unicode_literals

from whispy_lispy import (
    parser2, lexer, scopes2, interpreter2)


def get_ast_from_text2(text):
    """Return the abstract syntax tree for this source text

    :param str|unicode text: a text to be parsed into an Abstract syntax tree
    """
    return parser2.get_ast_from_cst(lexer.get_concrete_syntax_tree(
        lexer.get_flat_token_list(text)
    ))



def interpret_text2(text, scope):
    if scope is None:
        scope = scopes2.Scope()
    return interpreter2.interpret_ast(get_ast_from_text2(text), scope)