import signal
from math import log10, ceil

from .internal import argument_parser, csv_handling, plotting
from .internal import configuration as cfg
from .internal.util_classes import SampleRange


#
# Private helper functions for handling different subcommands
#

def __resolve_column_id(data_obj, col_id):
    # First interpret col_id as header name
    try:
        idx = data_obj.headers.index(col_id)
        return data_obj.headers[idx]
    except ValueError:
        pass

    # If col_id is no valid header name, try interpreting it as a column index.
    try:
        idx = int(col_id)
    except ValueError:
        return None

    if idx >= len(data_obj.headers):
        print(f'Given column index {idx} is out of range!')
        return None

    return data_obj.headers[idx]


def __handle_plot_args(args):
    # Make sure Ctrl+C in the terminal closes the plot
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sample_range = SampleRange(args.region[0], args.region[1],
                               args.divider)
    config = cfg.PlotConfig(args.filename, sample_range)

    data_obj = csv_handling.CsvData.from_file(config)
    if data_obj.size == 0:
        return

    for col_id in args.columns:
        col_name = __resolve_column_id(data_obj, col_id)
        if col_name is None:
            print(f'Unable to resolve column "{col_id}"! '
                  'Make sure you either pass a column name or an index!')
            continue

        config.add_column_to_subplot(cfg.ColumnConfig(
            col_name,
            data_obj.data[col_name]
        ))

    plotting.plot_csv_data(data_obj, config)


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
