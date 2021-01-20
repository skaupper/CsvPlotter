import signal
from math import log10, ceil

from .internal import argument_parser, csv_handling, plotting


#
# Private helper functions for handling different subcommands
#

def __handle_plot_args(args):
    # Make sure Ctrl+C in the terminal closes the plot
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    data_obj, start, end = csv_handling.read_data(args.filename, args.divide, args.region[0], args.region[1])
    if data_obj['size'] == 0:
        return

    plotting.plot_csv_data(data_obj, args.columns, start, end, args.divide)



def __handle_util_args(args):
    if args.list_headers:
        headers = csv_handling.read_headers(args.filename)
        print(f'Column headers found: {len(headers)}')
        idx_width = ceil(log10(len(headers)))
        for i, header in enumerate(headers):
            print(f'  {i:{idx_width}} : {header}')


#
# Public function which serve as application entrypoints
#

def plot():
    parser = argument_parser.create_plot_parser()
    args = parser.parse_args()
    __handle_plot_args(args)


def util():
    parser = argument_parser.create_utility_parser()
    args = parser.parse_args()
    __handle_util_args(args)


def combined():
    parser = argument_parser.create_combined_parser()
    args = parser.parse_args()

    chosen_command = args.chosen_command
    del args.chosen_command

    if chosen_command == 'plot':
        __handle_plot_args(args)
    elif chosen_command == 'util':
        __handle_util_args(args)
