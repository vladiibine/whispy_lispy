# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
import six
import re

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
            elif open_count == 0:
                new_tokens = get_tokens(remaining_text)
                atoms.extend(new_tokens)
                remaining_text = ''

    return atoms


TOKEN_TYPES = (
    (float, re.compile('[0-9]+\.[0-9]+')),
    (int, re.compile('[0-9]+')),
    (str, re.compile('[a-zA-Z_]+')),
    (get_atoms, re.compile('\(.*\)'))
)

def get_tokens(text):
    """Return nested list, representing the atoms in the given text

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

    return tokens
