# -*- coding utf-8 -*-
"""
Concrete syntax tree stuff

Lexer should return tokens that are instances of classes found here
"""
from __future__ import unicode_literals

class Token(object):
    """Concrete syntax tree node.

    Can represent a literal, operator, a name, or an atom.
    An atom is an ordered list of the previously mentioned elements
    """
    __slots__ = ['value']

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<T {}>'.format(self.value)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Token):
            return False
        return self.value == other.value

class ConcreteSyntaxNode(object):
    """A node in the concrete syntax tree.

    The state of this node is kept as a tuple
    """
    __slots__ = ['values']

    def __init__(self, values):
        """
        :type values: tuple
        """
        self.values = values

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        return self.values == other.values

    def __repr__(self):
        return '<cN {}>'.format(self.values)

    def is_root(self):
        return isinstance(self, RootConcreteSyntaxnode)

class RootConcreteSyntaxnode(ConcreteSyntaxNode):
    def __repr__(self):
        return '<RcN {}>'.format(self.values)

class NestingCommand(Token):
    """Represents a command to either increment or decrement the tree level
    """
    def __repr__(self):
        return '{}'.format(self.value[0])


IncrementNesting = NestingCommand(['<INC>'])

DecrementNesting = NestingCommand(['<DEC>'])

# No further use for the class
del NestingCommand
