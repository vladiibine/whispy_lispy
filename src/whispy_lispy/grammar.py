import re

from pyparsing import (
    Word, Keyword, NotAny, alphanums, nums, alphas, OneOrMore, srange,
    ZeroOrMore, Regex
)

from whispy_lispy import ast

int_literal = Word(nums) + NotAny('.')
int_literal.setParseAction(ast.Int.from_parsed_result)

float_literal = Word(nums) + Word('.') + Word(nums)
float_literal.setParseAction(ast.Float.from_parsed_result)

bool_literal = Keyword('#t') | Keyword('#f')
bool_literal.setParseAction(ast.Bool.from_parsed_result)

string_literal = Regex(r'\".*?(?<!\\)\"', re.DOTALL)
string_literal.setParseAction(ast.String.from_parse_result)

grammar = OneOrMore(float_literal | int_literal | bool_literal | string_literal)
