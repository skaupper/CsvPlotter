import argparse


#
# Argument type checkers
#

def __divide_check(v):
    # Only positive integers are allowed as a divider.

    error = True
    try:
        v = int(v)
        error = v < 1
    finally:
        if error:
            raise argparse.ArgumentTypeError('Positive integer expected')
    return v


def __region_check(v):
    # The region of samples to be plotted should be given in the form START:END.
    # Negative values for either of START or END represent the first resp. the last sample (i.e. a value of -1 for END
    # sets END to the index of the last sample).
    # Omitting either of the values will set its value to default (0 for START and -1 for END).

    error = True
    try:
        v = str(v)
        region = v.split(':')
        if len(region) != 2:
            raise argparse.ArgumentError()
        start = int(region[0]) if len(region[0]) > 0 else 0
        end = int(region[1]) if len(region[1]) > 0 else -1

        if start < 0:
            start = 0
        if end < 0:
            end = -1

        error = False
    finally:
        if error:
            raise argparse.ArgumentTypeError(
                'Region string of the form \'[START]:[END]\' expected')
    return (start, end)


#
# Private helpler functions
#

def __create_common_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('filename', help='CSV debug data')
    return parser


#
# Public parser generators
#

def create_plot_parser(generate_help=True):
    parser = argparse.ArgumentParser(description='Analyse the given CSV file.', parents=[
                                     __create_common_parser()], add_help=generate_help)

    parser.add_argument('columns', type=str, nargs='+',
                        help='A list of columns that should be plotted. Either the column name or index are valid.', default=[])
    parser.add_argument('-d', '--divider',      type=__divide_check,
                        help='Divides the input data to only take each nth packet', default=1)
    parser.add_argument('-r', '--region',       type=__region_check,     help='Specifies the desired data range in format \'START:END\' (both inclusive). '
                                                                              'START and END (or both) my be omitted to specify an open range '
                                                                              'e.g. use \'100:\' to plot all data from the 100th sample until the last one.', default=':')
    return parser


def create_utility_parser(generate_help=True):
    parser = argparse.ArgumentParser(description='Provide utilities to process a CSV file in different ways.', parents=[
                                     __create_common_parser()], add_help=generate_help)

    parser.add_argument('-l', '--list-headers', action='store_true',
                        help='List all column headers found (all entries of the first row).', default=False)
    return parser


def create_combined_parser():
    plot_parser = create_plot_parser(False)
    util_parser = create_utility_parser(False)

    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='chosen_command')
    sub_parsers.add_parser('plot', parents=[plot_parser])
    sub_parsers.add_parser('util', parents=[util_parser])
    return parser
