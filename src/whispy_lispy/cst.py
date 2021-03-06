# -*- coding utf-8 -*-
"""
Concrete syntax tree stuff

Lexer should return tokens that are instances of classes found here
"""
from __future__ import unicode_literals
import six


from whispy_lispy import keywords


class CSTError(Exception):
    pass


class Token(object):
    """Concrete syntax tree node.

    Can represent a literal, operator, a name, or an atom.
    An atom is an ordered list of the previously mentioned elements
    """
    __slots__ = ['value', 'source', 'index']

    def __init__(self, value, source=None, index=None):
        """
        :param value: the value of the token (python type)
        :param str source: the source code
        :param int index: the index of the token in the source code
        """
        self.value = value
        self.source = source
        self.index = index

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

    def is_operator(self):
        return (
            len(self.values) == 1 and
            self.values[0] in keywords.OPERATORS
        )

    def is_root(self):
        return isinstance(self, RootConcreteSyntaxnode)

    def is_leaf(self):
        return all(
            not isinstance(elem, ConcreteSyntaxNode) for elem in self.values)

    def is_symbol(self):
        return (
            len(self.values) == 1 and
            isinstance(self.values[0], six.string_types)
        )

    def is_int(self):
        return (
            len(self.values) == 1 and
            isinstance(self.values[0], int)
        )

    def is_float(self):
        return (
            len(self.values) == 1 and
            isinstance(self.values[0], float)
        )

    def is_bool(self):
        return (
            len(self.values) == 1 and
            isinstance(self.values[0], bool)
        )

    def is_string(self):
        return (
            len(self.values) == 1 and
            isinstance(self.values[0], six.string_types) and
            self.values[0][0] == '"' and
            self.values[0][-1] == '"'
        )

    def symbol_equals(self, param):
        if not self.is_symbol():
            raise CSTError('Node is not a symbol')
        return self.values[0] == param

    def symbol_in_iterable(self, iterable):
        for elem in iterable:
            if self.symbol_equals(elem):
                return True
        return False


class RootConcreteSyntaxnode(ConcreteSyntaxNode):
    def __repr__(self):
        return '<RcN {}>'.format(self.values)


class NestingCommand(Token):
    """Represents a command to either increment or decrement the tree level
    """
    def __repr__(self):
        return '{}'.format(self.value[0])

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value


class IncrementNesting(NestingCommand):
    def __init__(self, _=None, source=None, index=None):
        super(IncrementNesting, self).__init__(['<INC>'], source, index)


class DecrementNesting(NestingCommand):
    def __init__(self, _=None, source=None, index=None):
        super(DecrementNesting, self).__init__(['<DEC>'], source, index)
