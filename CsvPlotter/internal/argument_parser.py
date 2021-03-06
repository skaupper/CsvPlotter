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
    # Negative values for either of START or END represent the first resp. the last sample (i.e. a value of None for END
    # sets END to the index of the last sample).
    # Omitting either of the values will set its value to default (0 for START and None for END).

    if v is None:
        return None

    error = True
    try:
        v = str(v)
        region = v.split(':')
        if len(region) != 2:
            raise argparse.ArgumentError()
        start = int(region[0]) if len(region[0]) > 0 else 0
        end = int(region[1]) if len(region[1]) > 0 else None

        if start < 0:
            start = 0
        if end < 0:
            end = None

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
    return parser


#
# Public parser generators
#

def create_plot_parser(generate_help=True):
    parser = argparse.ArgumentParser(description='Plot the given CSV file.',
                                     parents=[__create_common_parser()], add_help=generate_help)

    parser.add_argument('-i', '--input-file',
                        help='CSV data file', required=False)
    parser.add_argument('columns', type=str, nargs='*',
                        help='A list of columns that should be plotted. Both the column name and index are valid.', default=[])
    parser.add_argument('-o', '--output-file', type=str,
                        help='If specified, stores the plot in a file and prevents opening a plot window.\nThe file '
                             'format is determined using the default behaviour of matplotlib.pyplot.savefig!', required=False)
    parser.add_argument('-d', '--divider',      type=__divide_check,
                        help='Divides the input data to only take each nth packet', required=False)
    parser.add_argument('-r', '--region',       type=__region_check,     help='Specifies the desired data range in format \'START:END\' (inclusive START but exclusive END). '
                                                                              'START and END (or both) my be omitted to specify an open range '
                                                                              'e.g. use \'100:\' to plot all data from the 100th sample until the last one.', required=False)
    parser.add_argument('-c', '--config', dest='yaml_config',  type=str,
                        help='Specifies a YAML plot configuration file to be used. This file is able to set all other settings'
                             ' like range and divider settings as well as the input and output files if desired.\nIf a configuration'
                             ' file is specified, passing additional columns plot them in a separate subplot. Explicitely passing'
                             ' other arguments to the script will override their values set in the configuration file.', required=False)
    return parser


def create_utility_parser(generate_help=True):
    parser = argparse.ArgumentParser(description='Provide utilities to process a CSV file in different ways.',
                                     parents=[__create_common_parser()], add_help=generate_help)

    parser.add_argument('input-file', help='CSV data file')
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
