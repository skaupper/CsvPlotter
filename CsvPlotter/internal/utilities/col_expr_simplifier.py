from .col_expr_parser import Literal, Value, FunctionCall, Assignment, ColRef, RowId

import math


#
# Actual math functions
#

def __apply_operator(op, arg1, arg2):
    OPS = {
        '+': lambda a1, a2: a1 + a2,
        '-': lambda a1, a2: a1 - a2,
        '*': lambda a1, a2: a1 * a2,
        '/': lambda a1, a2: a1 / a2 if a2 != 0 else math.nan,
        '%': lambda a1, a2: a1 % a2 if a2 != 0 else math.nan,
        '^': lambda a1, a2: a1 ** a2,
        # TODO: add more operators if necessary
    }

    if op not in OPS:
        raise KeyError(f'Unknown operator "{op}"')

    return OPS[op](arg1.value, arg2.value)


def __apply_function(func, arg):
    FUNCS = {
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
        # TODO: add more functions if necessary
    }

    if func not in FUNCS:
        raise KeyError(f'Unknown function "{func}"')

    return FUNCS[func](arg.value)


#
# Functions which are responsible for resolving runtime information
#

def __resolve_col_ref(value, csv_row):
    if csv_row is None:
        return value

    if value.name not in csv_row:
        raise KeyError(f'Unable to resolve column with name "{value.name}"')

    return Literal(float(csv_row[value.name]))


def __resolve_row_id(value, row_id):
    if row_id is None:
        return value
    return Literal(row_id)


#
# Recursive simplification functions
#

def __simplify_function_call(name, value, row_id, csv_row):
    arg = __simplify_value(value, row_id, csv_row)

    # The results of functions with literal arguments can be precalculated
    if isinstance(arg, Literal):
        return Literal(__apply_function(name, arg))

    return FunctionCall(name, arg)


def __simplify_value(value, row_id, csv_row):
    # Literals cannot be simplified further
    if isinstance(value, Literal):
        return value

    # Try to resolve column references and row IDs (if the needed information is provided)
    if isinstance(value, ColRef):
        return __resolve_col_ref(value, csv_row)
    if isinstance(value, RowId):
        return __resolve_row_id(value, row_id)

    # Try simplifying functions calls. In the best case it can be precalculated and stored as a literal.
    if isinstance(value, FunctionCall):
        return __simplify_function_call(value.name, value.argument, row_id, csv_row)

    # Otherwise, try to simplify both arguments of the given value
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

def simplify_expression(expr, row_id=None, csv_row=None):
    # Ignore the Assignment wrapper, if present
    if type(expr) == Assignment:
        expr.value = __simplify_value(expr.value, row_id, csv_row)
    else:
        expr = __simplify_value(expr, row_id, csv_row)
    return expr
