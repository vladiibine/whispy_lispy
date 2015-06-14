# -*- coding utf-8 -*-
"""
Main functions: `get_concrete_syntax_tree` and `get_token_list`

Call `get_concrete_syntax_tree` with the output of `get_token_list`
Call `get_token_list` with simple text (string, unicode, whatever)
"""
from __future__ import unicode_literals, absolute_import, print_function
import re
import six
from collections import deque

from whispy_lispy.exceptions import WhispyLispySyntaxError
from whispy_lispy import cst

if six.PY2:
    str = unicode
else:
    str = str


def make_token(func):
    def wrapper(value):
        return cst.Token(func(value))
    return wrapper


SOURCE_PATTERNS = (
    (make_token(lambda x: True if x == '#t' else False), re.compile('#[ft]')),
    (make_token(float), re.compile('[0-9]+\.[0-9]+')),
    (make_token(int), re.compile('[0-9]+')),
    # Matches escaped strings that can span multiple lines
    (make_token(str), re.compile(r'\".*?(?<!\\)\"', re.DOTALL)),
    # Match symbols and quotes
    (make_token(str), re.compile('[a-zA-Z_]+[0-9]*|\'')),
    (lambda _: cst.IncrementNesting, re.compile('\(')),
    (lambda _: cst.DecrementNesting, re.compile('\)')),
)


def get_flat_token_list(text):
    """From the source file, create a flat list of tokens"""
    tokens = []
    remaining_text = text.lstrip()

    while remaining_text:
        for converter, pattern in SOURCE_PATTERNS:
            result = pattern.match(remaining_text)
            if result:
                start, end = result.span()
                tokens.append(converter(remaining_text[start:end]))
                remaining_text = remaining_text[end:].lstrip()

    return tokens


def get_concrete_syntax_tree(token_list):
    """Return a "concrete" syntax tree from the flat token list

    Raises syntax error if braces are mismatched
    Collapses all the inc/dec tokens
    """
    q = deque([[]])

    for token in token_list:
        if token is cst.IncrementNesting:
            q.append([])
            continue
        if token is cst.DecrementNesting:
            wrap_up = q.pop()
            try:
                q[-1].append(cst.ConcreteSyntaxNode(tuple(wrap_up)))
            except IndexError:
                raise WhispyLispySyntaxError('Too many closing parentheses')
            continue
        q[-1].append(cst.ConcreteSyntaxNode((token.value,)))

    if len(q) > 1:
        raise WhispyLispySyntaxError('Too many opening parentheses')

    return cst.RootConcreteSyntaxnode(tuple(q[-1]))
