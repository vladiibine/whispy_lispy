# -*- coding utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
import six
import re

if six.PY2:
    str = unicode

TOKEN_TYPES = (
    (float, re.compile('[0-9]+\.[0-9]+')),
    (int, re.compile('[0-9]+')),
    (str, re.compile('[a-zA-Z_]+'))
)

def get_tokens(text):
    """Return nested list, representing the atoms in the given text

    :param text: a block of text (can contain newlines and everything)
    :rtype: list[str]
    """
    tokens = []
    for converter, pattern in TOKEN_TYPES:
        result = pattern.match(text)
        if result:
            tokens.append(converter(result.string))
            break

    return tokens
