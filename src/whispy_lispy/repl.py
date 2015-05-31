# -*- coding utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import six

if six.PY3:
    raw_input = input

from whispy_lispy import skip_steps, scopes, exceptions

PS1 = '(WL)$'
PS2 = '.....'
PS3 = '(WL):'


def repl():
    """Main REPL loop"""
    scope = scopes.Scope()
    while True:
        try:
            print(PS1, end=' ')
            text = get_user_input()
            try:
                result = skip_steps.interpret_text(text, scope)
                print(PS3, result, end='\n\n')
            except exceptions.BaseWhispyLispyError as err:
                print(err, end='\n\n')
        except KeyboardInterrupt:
            continue

        except EOFError:
            gracefully_exit()


def gracefully_exit():
    """Handle forced quit"""
    try:
        confirmation = None
        while confirmation not in ['y', 'n']:
            confirmation = raw_input('Really quit? (y/n)').lower()
        if confirmation == 'y':
            print()
            skip_steps.interpret_text('(quit)')
        else:
            return
    except EOFError:
        print()
        skip_steps.interpret_text('(quit)')


def get_user_input(parens_count=0, inside_string=False):
    """Get text from the user, to evaluate with the whispy_lispy interpreter

    If strings or braces are left open, will prompt for more text

    :param int parens_count: how many open parentheses(with no corresponding
        match) we've met so far
    :param bool inside_string: whether we're currently in a string literal
    :rtype: str | unicode
    """
    # symbols that would continue the input on the next line
    text = unicode(raw_input())
    while True:
        for idx, char in enumerate(text):
            if char == '"':
                if idx > 0 and text[idx - 1] != "\\":
                    inside_string = not inside_string
                if idx == 0:
                    inside_string = not inside_string
            if not inside_string:
                if char == '(':
                    parens_count += 1
                elif char == ')':
                    parens_count -= 1
        if parens_count == 0 and not inside_string:
            return text
        else:
            print(PS2, end=' ')
            return text + '\n' + get_user_input(parens_count, inside_string)
