# -*- coding utf-8 -*-
"""
Concrete syntax tree stuff

Lexer should return tokens that are instances of classes found here
"""
from __future__ import unicode_literals
import six

class CSTError(Exception):
    pass

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
        The tuple either contains other nodes, or values. Not both!
        :type values: tuple
        """
        types = set(type(elem) for elem in values)
        if len(types) > 1:
            raise CSTError(
                "Concrete Syntax Node should contain either other nodes, or "
                "simple values, not both. This node contains {} value(s): {}"
                .format(len(types), values)
            )
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

    def is_leaf(self):
        return all(
            not isinstance(elem, ConcreteSyntaxNode) for elem in self.values)

    def is_symbol(self):
        return (
            len(self.values) == 1 and
            isinstance(self.values[0], six.string_types) and
            not self.values[0] == '\''
        )

    def is_quote_literal(self):
        """Recognize the ' symbol"""
        return (
            len(self.values) == 1 and
            self.values[0] == '\''
        )

    def is_quote_function(self):
        """Recognize the `quote` function"""
        return (
            self.is_symbol() and
            self.values[0] == 'quote'
        )

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
