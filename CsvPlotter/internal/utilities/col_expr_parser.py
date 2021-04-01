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
# OPERATOR_1    = '+' | '-'
# VALUE_1       = VALUE_2 { OPERATOR_1 VALUE_2 }
#
# OPERATOR_2    = '*' | '/'
# VALUE_2       = VALUE_3 { OPERATOR_2 VALUE_3 }
#
# OPERATOR_3    = '%' | '^'
# VALUE_3       = VALUE_4 { OPERATOR_3 VALUE_4 }
#
# FUNCTION_CALL = IDENT '(' VALUE ')'
# COLUMN_REF    = '$' IDENT '$'
# ROW_ID        = '#'
# PAREN_VALUE   = '(' VALUE ')'
# CONSTANT      = IDENT
# VALUE_4       = FUNCTION_CALL | COLUMN_REF | LITERAL | ROW_ID | PAREN_VALUE | CONSTANT


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

    def __repr__(self):
        return f'ColRef{{name={self.name!r}}}'

    def dump(self, indent=0, incr=4):
        print(f'{" ": >{indent}}ColRef (name: {self.name})')


class FunctionCall(object):
    def __init__(self, name, argument):
        self.name = name
        self.argument = argument

    def __repr__(self):
        return f'FunctionCall{{name={self.name!r}, argument="{self.argument!r}"}}'

    def dump(self, indent=0, incr=4):
        print(f'{" ": >{indent}}FunctionCall (name: {self.name})')
        self.argument.dump(indent + incr)


class Literal(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Literal{{value={self.value!r}}}'

    def dump(self, indent=0, incr=4):
        print(f'{" ": >{indent}}Literal: {self.value}')


class RowId(object):
    def __repr__(self):
        return f'RowId{{}}'

    def dump(self, indent=0, incr=4):
        print(f'{" ": >{indent}}RowId: #')


class Operator(object):
    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return f'Operator{{op={self.op!r}}}'


class Constant(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Constant{{name={self.name!r}}}'


class Assignment(object):
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value

    def __repr__(self):
        return f'Assignment{{ident={self.ident!r}, value={self.value!r}}}'

    def dump(self, indent=0, incr=4):
        print(f'{" ": >{indent}}Assignment (target: {self.ident})')
        self.value.dump(indent + incr)


class Value(object):
    def __init__(self, arg1, op, arg2):
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2

    def __repr__(self):
        return f'Value{{arg1="{self.arg1!r}", op={self.op!r}, arg2="{self.arg2!r}"}}'

    def dump(self, indent=0, incr=4):
        print(f'{" ": >{indent}}Value (operator: {self.op.op})')
        self.arg1.dump(indent + incr)
        self.arg2.dump(indent + incr)


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

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if not(s[0].islower() or s[0].isupper() or is_underscore(s[0])):
        raise ColExprParseError(
            'Identifier did not start with a letter or an underscore', s)

    idx = 1
    if len(s) > 1:
        while s[idx].isalnum() or is_underscore(s[idx]):
            idx += 1

    return s[:idx], s[idx:].strip()


def __parse_number(s):
    ''' NUMBER = [0-9]+ '''
    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if not s[0].isdigit():
        raise ColExprParseError(
            'A number must start with a digit', s)

    idx = 1
    if len(s) > 1:
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
    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
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
    if len(s) > 0 and s[0] == '.':
        try:
            decimal, s = __parse_number(s[1:])
        except ColExprParseError as e:
            raise ColExprParseError(
                f'Failed to parse fractional part of literal: {e.message}', s)

        while decimal > 0:
            decimal /= 10.0

    # Parse exponent
    if len(s) > 0 and s[0] == 'e':
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
    return Literal(sign * (integer + decimal) * 10**exp), s


def __parse_function_call(s):
    ''' FUNCTION_CALL = IDENT '(' VALUE ')' '''
    name, s = __parse_ident(s)

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != '(':
        raise ColExprParseError(
            'The function call argument must be preceeded by an opening parenthesis', s)
    s = s[1:].strip()

    arg, s = __parse_value(s)

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != ')':
        raise ColExprParseError(
            'The function call argument must be preceeded by an closing parenthesis', s)
    s = s[1:].strip()

    return FunctionCall(name, arg), s


def __parse_column_ref(s):
    ''' COLUMN_REF = '$' IDENT '$' '''

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != '$':
        raise ColExprParseError(
            'A column reference must be started with a dollar sign', s)
    s = s[1:]

    name, s = __parse_ident(s)

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != '$':
        raise ColExprParseError(
            'A column reference must be ended with a dollar sign', s)
    s = s[1:]

    return ColRef(name), s


def __parse_row_id(s):
    ''' ROW_ID = '#' '''

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != '#':
        raise ColExprParseError('The row ID is designated using "#"', s)

    return RowId(), s[1:].strip()


def __parse_paren_value(s):
    ''' PAREN_VALUE = '(' VALUE ')' '''

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != '(':
        raise ColExprParseError(
            'A parenthesized value must start with "("', s)
    s = s[1:]

    val, s = __parse_value(s)

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)
    if s[0] != ')':
        raise ColExprParseError(
            'A parenthesized enclosed value must end with ")"', s)
    s = s[1:]

    return val, s


def __parse_constant(s):
    ''' CONSTANT = IDENT '''
    ident, s = __parse_ident(s)
    return Constant(ident), s


def __parse_value4(s):
    ''' VALUE_4 = FUNCTION_CALL | COLUMN_REF | LITERAL | ROW_ID | CONSTANT '''
    OPTIONS = [__parse_function_call, __parse_column_ref,
               __parse_literal, __parse_row_id, __parse_paren_value,
               __parse_constant]

    for o in OPTIONS:
        try:
            return o(s)
        except ColExprParseError:
            pass

    raise ColExprParseError('Could not find a match for VALUE_4', s)


def __parse_operator3(s):
    ''' OPERATOR_3 = '%' | '^' '''

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)

    OPS = ['%', '^']
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_1 but found "{s[0]}"', s)

    return Operator(s[0]), s[1:].strip()


def __parse_value3(s):
    ''' VALUE_3 = VALUE_4 { OPERATOR_3 VALUE_4 } '''
    val, s = __parse_value4(s)

    while True:
        try:
            op, tmp_s = __parse_operator3(s)
            val2, tmp_s = __parse_value4(tmp_s)
            s = tmp_s

            val = Value(val, op, val2)
        except ColExprParseError:
            break

    return val, s


def __parse_operator2(s):
    ''' OPERATOR_2 = '*' | '/' '''

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)

    OPS = ['*', '/']
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_2 but found "{s[0]}"', s)

    return Operator(s[0]), s[1:].strip()


def __parse_value2(s):
    ''' VALUE_2 = VALUE_3 { OPERATOR_2 VALUE_3 } '''
    val, s = __parse_value3(s)

    while True:
        try:
            op, tmp_s = __parse_operator2(s)
            val2, tmp_s = __parse_value3(tmp_s)
            s = tmp_s

            val = Value(val, op, val2)
        except ColExprParseError:
            break

    return val, s


def __parse_operator1(s):
    ''' OPERATOR_1 = '+' | '-' '''

    if len(s) == 0:
        raise ColExprParseError('Input string is empty', s)

    OPS = ['+', '-']
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_3 but found "{s[0]}"', s)

    return Operator(s[0]), s[1:].strip()


def __parse_value1(s):
    ''' VALUE_1 = VALUE_2 { OPERATOR_1 VALUE_2 } '''
    val, s = __parse_value2(s)

    while True:
        try:
            op, tmp_s = __parse_operator1(s)
            val2, tmp_s = __parse_value2(tmp_s)
            s = tmp_s

            val = Value(val, op, val2)
        except ColExprParseError:
            break

    return val, s


def __parse_value(s):
    ''' VALUE = VALUE_1 '''
    return __parse_value1(s)


def __parse_col_expr(s):
    ''' COL_EXPR = [ IDENT '=' ] VALUE '''

    # Try parsing [ IDENT '=' ]
    try:
        tmp_s = ''
        ident, tmp_s = __parse_ident(s)

        if len(tmp_s) == 0:
            raise ColExprParseError('Input string is empty', s)
        if tmp_s[0] != '=':
            raise ColExprParseError(
                'A COL_EXPR must separate its IDENT and VALUE using an equality sign', tmp_s)
        s = tmp_s[1:].strip()
    except ColExprParseError:
        ident = None

    value, s = __parse_value(s)

    if ident is None:
        return value, s
    return Assignment(ident, value), s


if __name__ == '__main__':
    s = 'new=1*4+2^5-7*2+sin(234)'
    expr = parse_col_expr(s)
    expr.dump()
