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


def make_token(func, node_type=cst.Token):
    """
    :param func: function to convert the found string into something else
    :param node_type: the type of the node to be created
    """
    def wrapper(value, source, index):
        """
        :param str value: a string from the source code that matched a pattern
        :param str source: the source code containing the value
        :param int index: the index of `value` in `source`
        :return: an instance of `node_type`, wrapping what `func` provided
        """
        return node_type(func(value), source, index)

    return wrapper


SOURCE_PATTERNS = (
    (make_token(lambda x: True if x == '#t' else False), re.compile('#[ft]')),
    (make_token(float), re.compile('[0-9]+\.[0-9]+')),
    (make_token(int), re.compile('[0-9]+')),
    # Matches escaped strings that can span multiple lines
    (make_token(str), re.compile(r'\".*?(?<!\\)\"', re.DOTALL)),
    # Match symbols and quotes
    (make_token(str), re.compile('[a-zA-Z_][a-zA-Z_0-9]*|\'')),
    # The parentheses
    (make_token(lambda x: None, cst.IncrementNesting), re.compile('\(')),
    (make_token(lambda x: None, cst.DecrementNesting), re.compile('\)')),
    # The operators
    (make_token(str, cst.Operator), re.compile(
        r'[\+\-\|&^~%]|[\*\\/=]{1,2}|[<>]=?|<<|>>|!='))
)


def get_flat_token_list(text):
    """From the source file, create a flat list of tokens"""
    tokens = []
    remaining_text = text.lstrip()
    last_iteration_text = remaining_text

    while remaining_text:
        for converter, pattern in SOURCE_PATTERNS:
            result = pattern.match(remaining_text)
            if result:
                start, end = result.span()
                tokens.append(converter(
                    remaining_text[start:end], text, text.index(remaining_text)))  # noqa
                remaining_text = remaining_text[end:].lstrip()
        if remaining_text == last_iteration_text:
            raise WhispyLispySyntaxError(
                text, text.index(remaining_text),
                "Character combination doesn't make sense")
        last_iteration_text = remaining_text

    return tokens


def make_parentheses_lispy(token_list):
    """When we decide to use the call style `func(args)` instead of
    `(func args)`, we'll use this function to seamlessly convert the syntax
    into proper lispy syntax

    :param list[cst.Token] token_list:
    :rtype: list[cst.Token]
    """
    # a(b((c d(((e f f(g h))))))) -> (a (b (c (d ( (e f (f g h)))))))
    new_tokens = []
    for i, token in enumerate(token_list[:-1]):
        if not isinstance(token, cst.NestingCommand):
            next_token = token_list[i + 1]
            if isinstance(next_token, cst.IncrementNesting):
                new_tokens.extend([next_token, token])

        if token not in new_tokens:
            new_tokens.append(token)
    new_tokens.append(token_list[-1])

    return new_tokens


def get_concrete_syntax_tree(token_list):
    """Return a "concrete" syntax tree from the flat token list

    Raises syntax error if braces are mismatched
    Collapses all the inc/dec tokens
    """
    q = deque([[]])

    for token in token_list:
        if isinstance(token, cst.IncrementNesting):
            q.append([])
            continue
        if isinstance(token, cst.DecrementNesting):
            wrap_up = q.pop()
            try:
                q[-1].append(cst.ConcreteSyntaxNode(tuple(wrap_up)))
            except IndexError:
                raise WhispyLispySyntaxError(
                    source=token.source, index=token.index,
                    extra_info='Too many closing parentheses')
            continue
        q[-1].append(cst.ConcreteSyntaxNode(
            (token.value,), isinstance(token, cst.Operator)))

    if len(q) > 1:
        raise WhispyLispySyntaxError(
            source=token.source, index=-1,
            extra_info='Too many opening parentheses. Close some.')

    return cst.RootConcreteSyntaxnode(tuple(q[-1]))
