import math
from typing import Dict, List, Optional, TypedDict
from .col_expr_parser import (
    Assignment,
    Literal,
    ValueType,
    parse_col_expr,
    ColExprParseError,
)
from .col_expr_simplifier import simplify_expression
from .. import csv_handling


class TransformedColumn(TypedDict):
    name: str
    expr: ValueType


#
# Public package entrypoint
#


def transform_file(
    input_file: Optional[str],
    output_file: str,
    expressions: List[str],
    row_count: Optional[int],
    include_input_columns: bool,
):
    # Preprocess the given expressions
    processed_expressions: List[Assignment] = []
    for expr in expressions:
        try:
            e = simplify_expression(parse_col_expr(expr))
            assert isinstance(e, Assignment)
            processed_expressions.append(e)
        except ColExprParseError:
            print(f'Failed to parse column expression "{expr}"')

    transformed_columns: List[TransformedColumn] = [
        {"name": a.ident, "expr": a.value} for a in processed_expressions
    ]

    with open(output_file, "w") as f:
        input_headers: List[str] = []

        def iteration_handler(i: int, row: List[str]) -> Optional[bool]:
            nonlocal input_headers
            nonlocal transformed_columns

            # Generate header row
            if i == 0:
                input_headers = [str(head).strip() for head in row]
                generated_headers = [c["name"] for c in transformed_columns]

                if include_input_columns:
                    f.write(", ".join(input_headers) + ", ")
                f.write(", ".join(generated_headers) + "\n")
                return

            data_index = i - 1

            # Prepare column data for the transformation expression to use their data
            col_data: Dict[str, float] = {}
            for i in range(len(row)):
                try:
                    col_data[input_headers[i]] = float(row[i])
                except ValueError:
                    col_data[input_headers[i]] = math.nan

            # TODO: allow to depend on not yet generated columns
            resolved_expressions: List[Literal] = []

            for c in transformed_columns:
                e = simplify_expression(c["expr"], data_index, col_data)
                if not isinstance(e, Literal):
                    raise TypeError("Resolved expressions must be of type Literal!")
                resolved_expressions.append(e)

            # Assemble given and generated data and write it to the output file
            input_row_data = row
            generated_row_data = [str(lit.value) for lit in resolved_expressions]
            if include_input_columns:
                f.write(", ".join([d.strip() for d in input_row_data]) + ", ")
            f.write(", ".join([d.strip() for d in generated_row_data]) + "\n")

        # Call the iteration handler using the given CSV file or the given row count
        if input_file is not None:
            csv_handling.CsvData.iterate_over_lines(input_file, iteration_handler)
        elif row_count is not None:
            for i in range(row_count + 1):
                iteration_handler(i, [])


if __name__ == "__main__":
    s = "diff_sin=$sin$ - $new_sin$"
    expr = parse_col_expr(s)
    expr.dump()
    print()
    simplify_expression(expr).dump()
    print()
