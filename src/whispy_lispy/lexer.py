# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
import re
import six
from collections import deque

from whispy_lispy.syntax import LispySyntaxError
from whispy_lispy import cst

if six.PY2:
    str = unicode


def get_atoms(text):
    """Return the "atom" as a possibly nested list

    An atom means the symbols surrounded by (), possibly containing other atoms

    :param text: text surrounded by with '(' at the start and ')' at the end
    :return:
    """
    # find all highest level atoms
    #  (eg. atom1="asdf" and atom2="dede (1 2)" from "(asdf)(dede (1 2))"
    # feed them to get_tokens
    remaining_text = text

    atoms = []
    while remaining_text:
        open_count = 0
        for idx, char in enumerate(remaining_text):
            if char == '(':
                open_count += 1
            elif char == ')':
                open_count -= 1
                if open_count == 0:
                    found_atom = remaining_text[1:idx].lstrip()
                    new_tokens = get_tokens(found_atom)
                    if new_tokens:
                        atoms.append(new_tokens)
                    remaining_text = remaining_text[idx + 1:].lstrip()
                    break
                elif open_count < 0:
                    raise LispySyntaxError(
                        'Atom contains too many closing parentheses: "{}"'
                        .format(text)
                    )
            elif open_count == 0:
                atoms.extend(get_tokens(remaining_text))
                remaining_text = ''
                break
            if len(text) == idx + 1:
                raise LispySyntaxError(
                    'Atom contains too many opening parentheses "{}"'
                    .format(text)
                )

    return atoms

def make_token(func):
    def wrapper(value):
        return cst.Token(func(value))
    return wrapper


TOKEN_TYPES = (
    (make_token(float), re.compile('[0-9]+\.[0-9]+')),
    (make_token(int), re.compile('[0-9]+')),
    # Match symbols and quotes
    (make_token(str), re.compile('[a-zA-Z_]+|\'')),
    (make_token(get_atoms), re.compile('\(.*\)'))
)

def get_tokens(text):
    """Return nested list, representing the atoms in the given text.

    I think this is a "syntax tree"...?

    :param text: a block of text (can contain newlines and everything)
    :rtype: list[str]
    """
    tokens = []
    remaining_text = text

    while remaining_text:
        for converter, pattern in TOKEN_TYPES:
            result = pattern.match(remaining_text)
            if result:
                start, end = result.span()
                new_tokens = converter(remaining_text[start:end])
                if not isinstance(new_tokens, list):
                    new_tokens = [new_tokens]
                tokens.extend(new_tokens)
                remaining_text = remaining_text[end:].lstrip()
                break
        else:
            raise LispySyntaxError(
                "The following structure can't be parsed: \"{}\"".format(
                    remaining_text
                )
            )

    return tokens

SOURCE_PATTERNS = (
    (make_token(lambda x: True if x == '#t' else False), re.compile('#[ft]')),
    (make_token(float), re.compile('[0-9]+\.[0-9]+')),
    (make_token(int), re.compile('[0-9]+')),
    # Match symbols and quotes
    (make_token(str), re.compile('[a-zA-Z_]+|\'')),
    (lambda _: cst.IncrementNesting, re.compile('\(')),
    (lambda _: cst.DecrementNesting, re.compile('\)')),
)

def get_flat_token_list(text):
    """From the source file, create a flat list of tokens
    """
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
                raise LispySyntaxError('Too many closing parentheses')
            continue
        q[-1].append(cst.ConcreteSyntaxNode((token.value,)))

    if len(q) > 1:
        raise LispySyntaxError('Too many opening parentheses')

    return cst.ConcreteSyntaxNode(tuple(q[-1]))
