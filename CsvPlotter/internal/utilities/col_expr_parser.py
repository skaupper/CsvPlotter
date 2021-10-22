# Expression Grammar:
#
# COL_NAME = [a-zA-Z_0-9()][a-zA-Z_0-9() ]*
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
# COLUMN_REF    = '$' COL_NAME '$'
# ROW_ID        = '#'
# PAREN_VALUE   = '(' VALUE ')'
# CONSTANT      = IDENT
# VALUE_4       = FUNCTION_CALL | COLUMN_REF | LITERAL | ROW_ID | PAREN_VALUE | CONSTANT


from dataclasses import dataclass
from typing import Optional, Tuple, Union


#
# Interface classes and functions
#


class ColExprParseError(Exception):
    def __init__(self, message: str, remaining_string: str):
        self.message = message
        self.remaining_string = remaining_string
        super().__init__(self.message)


ValueType = Union["Value", "Constant", "RowId", "ColRef", "Literal", "FunctionCall"]


@dataclass
class ColRef:
    name: str

    def dump(self, indent: int = 0, incr: int = 4):
        print(f'{" ": >{indent}}ColRef (name: {self.name})')


@dataclass
class FunctionCall:
    name: str
    argument: ValueType

    def dump(self, indent: int = 0, incr: int = 4):
        print(f'{" ": >{indent}}FunctionCall (name: {self.name})')
        self.argument.dump(indent + incr)


@dataclass
class Literal:
    value: float

    def dump(self, indent: int = 0, incr: int = 4):
        print(f'{" ": >{indent}}Literal: {self.value}')


@dataclass
class RowId:
    def dump(self, indent: int = 0, incr: int = 4):
        print(f'{" ": >{indent}}RowId: #')


@dataclass
class Operator:
    op: str


@dataclass
class Constant:
    name: str

    def dump(self, indent: int = 0, incr: int = 4):
        print(f'{" ": >{indent}}Constant: #')


@dataclass
class Value:
    arg1: ValueType
    op: Optional[Operator]
    arg2: Optional[ValueType]

    def dump(self, indent: int = 0, incr: int = 4):
        print(
            f'{" ": >{indent}}Value (operator: '
            f'{self.op.op if self.op is not None else ""})'
        )

        self.arg1.dump(indent + incr)
        if self.arg2 is not None:
            self.arg2.dump(indent + incr)


@dataclass
class Assignment:
    ident: str
    value: ValueType

    def dump(self, indent: int = 0, incr: int = 4):
        print(f'{" ": >{indent}}Assignment (target: {self.ident})')
        self.value.dump(indent + incr)


def parse_col_expr(s: str) -> Union[Assignment, ValueType]:
    expr, s = __parse_col_expr(s)
    if len(s) > 0:
        raise ColExprParseError(
            "Column expression did not consume the whole input string", s
        )

    return expr


#
# Internal parse implementation
#


def __parse_col_name(s: str) -> Tuple[str, str]:
    """COL_NAME[a-zA-Z_0-9()][a-zA-Z_0-9() ]*"""

    def is_underscore(c: str) -> bool:
        return c == "_"

    def is_paren(c: str) -> bool:
        return c == "(" or c == ")"

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if not (s[0].isalnum() or is_underscore(s[0]) or is_paren(s[0])):
        raise ColExprParseError(
            "Identifier did not start with a letter or an underscore", s
        )

    idx = 1
    if len(s) > 1:
        while len(s) > idx and (
            s[idx].isalnum()
            or is_underscore(s[idx])
            or is_paren(s[idx])
            or s[idx] == " "
        ):
            idx += 1

    return s[:idx], s[idx:].strip()


def __parse_ident(s: str) -> Tuple[str, str]:
    """IDENT = [a-zA-Z_][a-zA-Z_0-9]*"""

    def is_underscore(c: str) -> bool:
        return c == "_"

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if not (s[0].islower() or s[0].isupper() or is_underscore(s[0])):
        raise ColExprParseError(
            "Identifier did not start with a letter or an underscore", s
        )

    idx = 1
    if len(s) > 1:
        while len(s) > idx and (s[idx].isalnum() or is_underscore(s[idx])):
            idx += 1

    return s[:idx], s[idx:].strip()


def __parse_number(s: str) -> Tuple[int, str]:
    """NUMBER = [0-9]+"""
    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if not s[0].isdigit():
        raise ColExprParseError("A number must start with a digit", s)

    idx = 1
    if len(s) > 1:
        while s[idx].isdigit():
            idx += 1

    return int(s[:idx]), s[idx:].strip()


def __parse_literal(s: str) -> Tuple[Literal, str]:
    """LITERAL = \\-?[0-9]+(\\.[0-9]+)?(e\\-?[0-9]+)?"""
    sign = 1
    exp = 0
    integer = 0
    decimal = 0

    # Parse sign
    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] == "-":
        sign = -1
        s = s[1:]
    elif s[0] == "+":
        sign = 1
        s = s[1:]

    # Parse integer part
    try:
        integer, s = __parse_number(s)
    except ColExprParseError as e:
        raise ColExprParseError(
            f"Failed to parse integer part of literal: {e.message}", s
        )

    # Parse fractional part
    if len(s) > 0 and s[0] == ".":
        try:
            decimal, s = __parse_number(s[1:])
        except ColExprParseError as e:
            raise ColExprParseError(
                f"Failed to parse fractional part of literal: {e.message}", s
            )

        while decimal > 0:
            decimal /= 10.0

    # Parse exponent
    if len(s) > 0 and s[0] == "e":
        s = s[1:]

        # Parse sign of exponent
        exp_sign = 1
        if s[0] == "-":
            exp_sign = -1
            s = s[1:]
        elif s[0] == "+":
            s = s[1:]

        exp, s = __parse_number(s)
        exp *= exp_sign

    # Assemble literal
    return Literal(sign * (integer + decimal) * 10 ** exp), s


def __parse_function_call(s: str) -> Tuple[FunctionCall, str]:
    """FUNCTION_CALL = IDENT '(' VALUE ')'"""
    name, s = __parse_ident(s)

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != "(":
        raise ColExprParseError(
            "The function call argument must be preceeded by an opening parenthesis", s
        )
    s = s[1:].strip()

    arg, s = __parse_value(s)

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != ")":
        raise ColExprParseError(
            "The function call argument must be preceeded by an closing parenthesis", s
        )
    s = s[1:].strip()

    return FunctionCall(name, arg), s


def __parse_column_ref(s: str) -> Tuple[ColRef, str]:
    """COLUMN_REF = '$' IDENT '$'"""

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != "$":
        raise ColExprParseError(
            "A column reference must be started with a dollar sign", s
        )
    s = s[1:]

    name, s = __parse_col_name(s)

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != "$":
        raise ColExprParseError(
            "A column reference must be ended with a dollar sign", s
        )
    s = s[1:]

    return ColRef(name), s


def __parse_row_id(s: str) -> Tuple[RowId, str]:
    """ROW_ID = '#'"""

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != "#":
        raise ColExprParseError('The row ID is designated using "#"', s)

    return RowId(), s[1:].strip()


def __parse_paren_value(s: str) -> Tuple[ValueType, str]:
    """PAREN_VALUE = '(' VALUE ')'"""

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != "(":
        raise ColExprParseError('A parenthesized value must start with "("', s)
    s = s[1:]

    val, s = __parse_value(s)

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)
    if s[0] != ")":
        raise ColExprParseError('A parenthesized enclosed value must end with ")"', s)
    s = s[1:]

    return val, s


def __parse_constant(s: str) -> Tuple[Constant, str]:
    """CONSTANT = IDENT"""
    ident, s = __parse_ident(s)
    return Constant(ident), s


def __parse_value4(s: str) -> Tuple[ValueType, str]:
    """VALUE_4 = FUNCTION_CALL | COLUMN_REF | LITERAL | ROW_ID | CONSTANT"""
    OPTIONS = [
        __parse_function_call,
        __parse_column_ref,
        __parse_literal,
        __parse_row_id,
        __parse_paren_value,
        __parse_constant,
    ]

    for o in OPTIONS:
        try:
            return o(s)
        except ColExprParseError:
            pass

    raise ColExprParseError("Could not find a match for VALUE_4", s)


def __parse_operator3(s: str) -> Tuple[Operator, str]:
    """OPERATOR_3 = '%' | '^'"""

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)

    OPS = ["%", "^"]
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_1 but found "{s[0]}"', s)

    return Operator(s[0]), s[1:].strip()


def __parse_value3(s: str) -> Tuple[ValueType, str]:
    """VALUE_3 = VALUE_4 { OPERATOR_3 VALUE_4 }"""
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


def __parse_operator2(s: str) -> Tuple[Operator, str]:
    """OPERATOR_2 = '*' | '/'"""

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)

    OPS = ["*", "/"]
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_2 but found "{s[0]}"', s)

    return Operator(s[0]), s[1:].strip()


def __parse_value2(s: str) -> Tuple[ValueType, str]:
    """VALUE_2 = VALUE_3 { OPERATOR_2 VALUE_3 }"""
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


def __parse_operator1(s: str) -> Tuple[Operator, str]:
    """OPERATOR_1 = '+' | '-'"""

    if len(s) == 0:
        raise ColExprParseError("Input string is empty", s)

    OPS = ["+", "-"]
    if s[0] not in OPS:
        raise ColExprParseError(f'Expected OPERATOR_3 but found "{s[0]}"', s)

    return Operator(s[0]), s[1:].strip()


def __parse_value1(s: str) -> Tuple[ValueType, str]:
    """VALUE_1 = VALUE_2 { OPERATOR_1 VALUE_2 }"""
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


def __parse_value(s: str) -> Tuple[ValueType, str]:
    """VALUE = VALUE_1"""
    return __parse_value1(s)


def __parse_col_expr(s: str) -> Tuple[Union[Assignment, ValueType], str]:
    """COL_EXPR = [ IDENT '=' ] VALUE"""

    # Try parsing [ IDENT '=' ]
    try:
        tmp_s = ""
        ident, tmp_s = __parse_ident(s)

        if len(tmp_s) == 0:
            raise ColExprParseError("Input string is empty", s)
        if tmp_s[0] != "=":
            raise ColExprParseError(
                "A COL_EXPR must separate its IDENT and VALUE using an equality sign",
                tmp_s,
            )
        s = tmp_s[1:].strip()
    except ColExprParseError:
        ident = None

    value, s = __parse_value(s)

    if ident is None:
        return value, s
    return Assignment(ident, value), s


if __name__ == "__main__":
    s = "new=1*4+2^5-7*2+sin(234)"
    expr = parse_col_expr(s)
    expr.dump()
