from whispy_lispy import grammar, types
import pyparsing


def test_int_literal_simple():
    assert grammar.int_literal.parseString('1234')[0] == types.Int((1234,))


def test_dont_parse_int_literal_before_period():
    try:
        grammar.int_literal.parseString('1234.')
    except pyparsing.ParseException:
        pass


def test_dont_parse_int_when_float_matches():
    try:
        grammar.int_literal.parseString('1234.1')
    except pyparsing.ParseException:
        pass


def test_parse_float_literal_simple():
    assert grammar.float_literal.parseString('123.44')[0] == types.Float((123.44,))


def test_bool():
    assert grammar.bool_literal.parseString('#t')[0] == types.Bool((True,))
    assert grammar.bool_literal.parseString('#f')[0] == types.Bool((False,))


def test_string_no_quotes_xx():
    raw_string = 'dd ff gg \n lol;`12*&^%*^%:'
    string = '"' + raw_string + '"'
    assert grammar.string_literal.parseString(string)[0] == types.String((raw_string,))


def test_string_with_quotes():
    raw_string = r"""a\"b\"c\"\"\"\"\\\""""
    string = '"' + raw_string + '"'
    assert grammar.string_literal.parseString(string)[0] == types.String((raw_string,))


def test_parse_int_float():
    string = '11 22.3'
    result = grammar.grammar.parseString(string)

    assert result[0] == types.Int((11,))
    assert result[1] == types.Float((22.3,))


def test_parse_multiple_ints_and_floats():
    string = '1 2.2 2.3 1 1 4.5'
    result = grammar.grammar.parseString(string)

    assert result[0] == types.Int((1,))
    assert result[1] == types.Float((2.2,))
    assert result[2] == types.Float((2.3,))
    assert result[3] == types.Int((1,))
    assert result[4] == types.Int((1,))
    assert result[5] == types.Float((4.5,))


def test_parse_all_types_xx():
    string = r'"1.1" 1 1.1 #f "\#f" "\""'
    result = grammar.grammar.parseString(string)

    assert result[0] == types.String(("1.1",))
    assert result[1] == types.Int((1,))
    assert result[2] == types.Float((1.1,))
    assert result[3] == types.Bool((False,))
    assert result[4] == types.String((r"\#f",))
    assert result[5] == types.String((r'\"',))
