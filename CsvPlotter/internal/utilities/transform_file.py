from .col_expr_parser import Literal, parse_col_expr, ColExprParseError
from .col_expr_simplifier import simplify_expression
from .. import csv_handling

#
# Public package entrypoint
#


def transform_file(input_file, output_file, expressions, row_count):
    # Preprocess the given expressions
    processed_expressions = []
    for expr in expressions:
        try:
            processed_expressions.append(
                simplify_expression(parse_col_expr(expr)))
        except ColExprParseError:
            print(f'Failed to parse column expression "{expr}"')

    transformed_columns = [{'name': a.ident, 'expr': a.value}
                           for a in processed_expressions]

    with open(output_file, 'w') as f:
        headers = None

        def iteration_handler(i, row):
            nonlocal headers
            nonlocal transformed_columns

            # Generate header row
            if i == 0:
                headers = [str(head).strip() for head in row] + \
                    [c['name'] for c in transformed_columns]
                f.write(', '.join(headers) + '\n')
                return

            data_index = i-1

            # Prepare column data for the transformation expression to use their data
            col_data = {}
            for i in range(len(row)):
                col_data[headers[i]] = row[i]

            # TODO: allow to depend on not yet generated columns
            resolved_expressions = [simplify_expression(c['expr'], data_index, col_data)
                                    for c in transformed_columns]

            # Sanity checks
            if not all([isinstance(v, Literal) for v in resolved_expressions]):
                raise TypeError(
                    'Resolved expressions must be of type Literal!')

            # Assemble given and generated data and write it to the output file
            full_row_data = row + [lit.value for lit in resolved_expressions]
            f.write(', '.join([str(d).strip() for d in full_row_data]) + '\n')

        # Call the iteration handler using the given CSV file or the given row count
        if input_file is not None:
            csv_handling.CsvData.iterate_over_lines(
                input_file, iteration_handler)
        elif row_count is not None:
            for i in range(row_count+1):
                iteration_handler(i, [])


if __name__ == '__main__':
    s = 'diff_sin=$sin$ - $new_sin$'
    expr = parse_col_expr(s)
    expr.dump()
    print()
    simplify_expression(expr).dump()
    print()
