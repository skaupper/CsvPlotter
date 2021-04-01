from typing import Callable, Dict, Optional, Union
from .col_expr_parser import Literal, Value, FunctionCall, Assignment, ColRef, RowId, Constant, ValueType

import math


#
# Actual math functions
#

def __apply_operator(op: str, arg1: Literal, arg2: Literal) -> float:
    OPS: Dict[str, Callable[[float, float], float]] = {
        '+': lambda a1, a2: a1 + a2,
        '-': lambda a1, a2: a1 - a2,
        '*': lambda a1, a2: a1 * a2,
        '/': lambda a1, a2: a1 / a2 if a2 != 0 else math.nan,
        '%': lambda a1, a2: a1 % a2 if a2 != 0 else math.nan,
        '^': lambda a1, a2: a1 ** a2,
    }

    if op not in OPS:
        raise KeyError(f'Unknown operator "{op}"')

    return OPS[op](arg1.value, arg2.value)


def __apply_function(func: str, arg: Literal) -> float:
    FUNCS: Dict[str, Callable[[float], float]] = {
        'sin': lambda a: math.sin(a),
        'cos': lambda a: math.cos(a),
        'tan': lambda a: math.tan(a),
        'sqrt': lambda a: math.sqrt(a) if a >= 0 else math.nan,
        'ln': lambda a: math.log(a) if a > 0 else math.nan,
        'lg': lambda a: math.log10(a) if a > 0 else math.nan,
        'lb': lambda a: math.log2(a) if a > 0 else math.nan,
        'log': lambda a: math.log(a) if a > 0 else math.nan,
        'log10': lambda a: math.log10(a) if a > 0 else math.nan,
        'log2': lambda a: math.log2(a) if a > 0 else math.nan,
    }

    if func not in FUNCS:
        raise KeyError(f'Unknown function "{func}"')

    return FUNCS[func](arg.value)


def __apply_constant(const: str) -> float:
    CONSTANTS = {
        'e': math.e,
        'pi': math.pi,
        'tau': math.tau,
        'inf': math.inf,
        'nan': math.nan
    }

    const = const.lower()

    if const not in CONSTANTS:
        raise KeyError(f'Unknown Constant "{const}"')

    return CONSTANTS[const]


#
# Functions which are responsible for resolving runtime information
#

def __resolve_col_ref(value: ColRef, csv_row: Optional[Dict[str, float]]) -> Union[ColRef, Literal]:
    if csv_row is None:
        return value

    if value.name not in csv_row:
        raise KeyError(f'Unable to resolve column with name "{value.name}"')

    return Literal(float(csv_row[value.name]))


def __resolve_row_id(value: RowId, row_id: Optional[int]) -> Union[RowId, Literal]:
    if row_id is None:
        return value
    return Literal(row_id)


#
# Recursive simplification functions
#

def __simplify_function_call(name: str, value: ValueType, row_id: Optional[int], csv_row: Optional[Dict[str, float]]) -> Union[Literal, FunctionCall]:
    arg = __simplify_value(value, row_id, csv_row)

    # The results of functions with literal arguments can be precalculated
    if isinstance(arg, Literal):
        return Literal(__apply_function(name, arg))

    return FunctionCall(name, arg)


def __simplify_value(value: ValueType, row_id: Optional[int], csv_row: Optional[Dict[str, float]]) -> ValueType:
    # Literals cannot be simplified further
    if isinstance(value, Literal):
        return value

    # Try to resolve column references and row IDs (if the needed information is provided)
    if isinstance(value, ColRef):
        return __resolve_col_ref(value, csv_row)
    if isinstance(value, RowId):
        return __resolve_row_id(value, row_id)

    # Try to resolve a constant
    if isinstance(value, Constant):
        return Literal(__apply_constant(value.name))

    # Try simplifying functions calls. In the best case it can be precalculated and stored as a literal.
    if isinstance(value, FunctionCall):
        return __simplify_function_call(value.name, value.argument, row_id, csv_row)

    # Otherwise, try to simplify both arguments of the given value
    assert isinstance(value, Value)
    assert value.arg2 is not None and value.op is not None
    simple_arg1 = __simplify_value(value.arg1, row_id, csv_row)
    simple_arg2 = __simplify_value(value.arg2, row_id, csv_row)

    # If the simplified arguments result in literals, precalculate the result of operation
    if isinstance(simple_arg1, Literal) and isinstance(simple_arg2, Literal):
        return Literal(__apply_operator(value.op.op, simple_arg1, simple_arg2))

    # Otherwise, return a new value
    return Value(simple_arg1, value.op, simple_arg2)


#
# Public simplification entrypoint
#

def simplify_expression(expr: Union[ValueType, Assignment], row_id: Optional[int] = None, csv_row: Optional[Dict[str, float]] = None) -> Union[ValueType, Assignment]:
    # Ignore the Assignment wrapper, if present
    if isinstance(expr, Assignment):
        expr.value = __simplify_value(expr.value, row_id, csv_row)
    else:
        expr = __simplify_value(expr, row_id, csv_row)
    return expr
