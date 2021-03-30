# Expression Grammar:
#
# IDENT = [a-zA-Z_][a-zA-Z_0-9]*
# NUMBER = [0-9]+
# LITERAL = [-+]?[0-9]+(\.[0-9]+)?(e\-?[0-9]+)?
#
# COL_EXPR      = [ IDENT '=' ] VALUE
#
# VALUE         = VALUE_1
#
# OPERATOR_1    = '%' | '^'
# VALUE_1       = VALUE_2 [ OPERATOR_1 VALUE_1 ]
#
# OPERATOR_2    = '*' | '/'
# VALUE_2       = VALUE_3 [ OPERATOR_2 VALUE_1 ]
#
# OPERATOR_3    = '+' | '-'
# VALUE_3       = VALUE_4 [ OPERATOR_3 VALUE_1 ]
#
# FUNCTION_CALL = IDENT '(' VALUE ')'
# COLUMN_REF    = '$' IDENT '$'
# VALUE_4       = FUNCTION_CALL | COLUMN_REF | LITERAL


#
# Interface classes and functions
#

class ColExprParseError(Exception):
    def __init__(self, message, remaining_string):
        self.message = message
        self.remaining_string = remaining_string
        super().__init__(self.message)


class ColRef(object):
    def __init__(self, name):
        self.name = name


class FunctionCall(object):
    def __init__(self, name, argument):
        self.name = name
        self.argument = argument


def parse_col_expr(s):
    expr, s = __parse_col_expr(s)
    if len(s) > 0:
        raise ColExprParseError(
            'Column expression did not consume the whole input string', s)

    return expr


#
# Internal parse implementation
#

def __parse_ident(s):
    ''' IDENT = [a-zA-Z_][a-zA-Z_0-9]* '''

    def is_underscore(c):
        return c == '_'

    if not(s[0].islower() or s[0].isupper() or is_underscore(s[0])):
        raise ColExprParseError(
            'Identifier did not start with a letter or an underscore', s)

    i = 1
    while s[i].isalnum() or is_underscore(s[i]):
        i += 1

    return s[:i], s[i:].strip()


def __parse_number(s):
    if not s[0].isdigit():
        raise ColExprParseError(
            'A number must start with a digit', s)

    idx = 1
    while s[idx].isdigit():
        idx += 1

    return int(s[:idx]), s[idx:].strip()


def __parse_literal(s):
    ''' LITERAL = \-?[0-9]+(\.[0-9]+)?(e\-?[0-9]+)? '''
    sign = 1
    exp = 0
    integer = 0
    decimal = 0

    # Parse sign
    if s[0] == '-':
        sign = -1
        s = s[1:]
    elif s[0] == '+':
        sign = 1
        s = s[1:]

    # Parse integer part
    try:
        integer, s = __parse_number(s)
    except ColExprParseError as e:
        raise ColExprParseError(
            f'Failed to parse integer part of literal: {e.message}', s)

    # Parse fractional part
    if s[0] == '.':
        try:
            decimal, s = __parse_number(s[1:])
        except ColExprParseError as e:
            raise ColExprParseError(
                f'Failed to parse fractional part of literal: {e.message}', s)

        while decimal > 0:
            decimal /= 10.0

    # Parse exponent
    if s[0] == 'e':
        s = s[1:]

        # Parse sign of exponent
        exp_sign = 1
        if s[0] == '-':
            exp_sign = -1
            s = s[1:]
        elif s[0] == '+':
            s = s[1:]

        exp, s = __parse_number(s)
        exp *= exp_sign

    # Assemble literal
    return sign * (integer + decimal) * 10**exp, s


def __parse_function_call(s):
    ''' FUNCTION_CALL = IDENT '(' VALUE ')' '''
    name, s = __parse_ident(s)

    if s[0] != '(':
        raise ColExprParseError(
            'The function call argument must be preceeded by an opening parenthesis', s)
    s = s[1:].strip()

    arg, s = __parse_value(s)

    if s[0] != ')':
        raise ColExprParseError(
            'The function call argument must be preceeded by an closing parenthesis', s)
    s = s[1:].strip()

    return FunctionCall(name, arg), s


def __parse_column_ref(s):
    ''' COLUMN_REF = '$' IDENT '$' '''
    if s[0] != '$':
        raise ColExprParseError(
            'A column reference must be started with a dollar sign', s)
    s = s[1:]

    name, s = __parse_ident(s)

    if s[0] != '$':
        raise ColExprParseError(
            'A column reference must be ended with a dollar sign', s)
    s = s[1:]

    return ColRef(name), s


def __parse_value4(s):
    ''' VALUE_4 = FUNCTION_CALL | COLUMN_REF | LITERAL '''
    OPTIONS = [__parse_function_call, __parse_column_ref, __parse_literal]

    for o in OPTIONS:
        try:
            return o(s)
        except ColExprParseError:
            pass

    raise ColExprParseError('Could not find a match for VALUE_4', s)


def __parse_operator3(s):
    ''' OPERATOR_3 = '+' | '-' '''

    OPS = ['*', '/']
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_3 but found "{s[0]}"', s)

    return s[0], s[1:].strip()


def __parse_value3(s):
    ''' VALUE_3 = VALUE_4 [ OPERATOR_3 VALUE_1 ] '''
    val1, s = __parse_value4(s)
    try:
        op, tmp_s = __parse_operator3(s)
        val2, tmp_s = __parse_value1(tmp_s)
        s = tmp_s
    except ColExprParseError:
        op = None
        val2 = None

    return (val1, op, val2), s


def __parse_operator2(s):
    ''' OPERATOR_2 = '*' | '/' '''

    OPS = ['*', '/']
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_2 but found "{s[0]}"', s)

    return s[0], s[1:].strip()


def __parse_value2(s):
    ''' VALUE_2 = VALUE_3 [ OPERATOR_2 VALUE_1 ] '''
    val1, s = __parse_value3(s)
    try:
        op, tmp_s = __parse_operator2(s)
        val2, tmp_s = __parse_value1(tmp_s)
        s = tmp_s
    except ColExprParseError:
        op = None
        val2 = None

    return (val1, op, val2), s


def __parse_operator1(s):
    ''' OPERATOR_1 = '%' | '^' '''

    OPS = ['%', '^']
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_1 but found "{s[0]}"', s)

    return s[0], s[1:].strip()


def __parse_value1(s):
    ''' VALUE_1 = VALUE_2 [ OPERATOR_1 VALUE_2 ] '''
    val1, s = __parse_value2(s)
    try:
        op, tmp_s = __parse_operator1(s)
        val2, tmp_s = __parse_value1(tmp_s)
        s = tmp_s
    except ColExprParseError:
        op = None
        val2 = None

    return (val1, op, val2), s


def __parse_value(s):
    ''' VALUE = VALUE_1 '''
    return __parse_value1(s)


def __parse_col_expr(s):
    ''' COL_EXPR = [ IDENT '=' ] VALUE '''

    # Try parsing [ IDENT '=' ]
    try:
        tmp_s = ''
        ident, tmp_s = __parse_ident(s)
        if tmp_s[0] != '=':
            raise ColExprParseError(
                'A COL_EXPR must separate its IDENT and VALUE using an equality sign')
        s = tmp_s[1:].strip()
    except ColExprParseError:
        ident = None

    value, s = __parse_value(s)
    return (ident, value), s


if __name__ == '__main__':
    s = 'diff_sin=$sin$ - $new_sin$'
    print(f'Orig : {s}')
    ident, s = __parse_ident(s)
    print(f'Ident: {ident}')
    print(f'Rem  : {s}')
