import yaml

from .internal import argument_parser, csv_handling, plotting
from .internal import configuration as cfg
from .internal.utils import Range


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
    if 'yaml_config' in args and args.yaml_config is not None:
        # Construct config from YAML file and update values with command line arguments
        try:
            with open(args.yaml_config, 'r') as f:
                yaml_config = yaml.safe_load(f)
        except yaml.YAMLError as ex:
            print(f'Failed to load config file "{args.yaml_config}": {ex}')
            return

        plot_cfg = cfg.PlotConfig.from_obj(yaml_config)

        if 'input_file' in args and args.input_file is not None:
            if len(args.input_file) == 0:
                plot_cfg.input_file = None
            else:
                plot_cfg.input_file = args.input_file
        if 'output_file' in args and args.output_file is not None:
            if len(args.output_file) == 0:
                plot_cfg.output_file = None
            else:
                plot_cfg.output_file = args.output_file
        if 'region' in args and args.region is not None:
            plot_cfg.range.start = args.region[0]
            plot_cfg.range.end = args.region[1] + \
                1 if args.region[1] is not None else None
        if 'divider' in args and args.divider is not None:
            plot_cfg.range.divider = args.divider

    else:
        # Construct config from command line arguments
        plot_cfg = cfg.PlotConfig.from_obj({
            'input_file': args.input_file,
            'output_file': args.output_file,
            'range_start': args.region[0] if args.region is not None else None,
            'range_end': args.region[1] if args.region is not None else None,
            'divider': args.divider,
        })

    # Validity checks
    if plot_cfg.input_file is None or len(plot_cfg.input_file) == 0:
        raise ValueError(f'No input file is specified!')

    # Load data into RAM
    data_obj = csv_handling.CsvData.from_file(plot_cfg)
    if data_obj.size == 0:
        return

    # Resolve column identifiers given as command line arguments and add the constructed subplot
    if len(args.columns) > 0:
        subplot_cfg = cfg.SubplotConfig()
        for col_id in args.columns:
            col_name = __resolve_column_id(data_obj, col_id)
            if col_name is None:
                print(f'Unable to resolve column "{col_id}"! '
                      'Make sure you either pass a column name or an index!')
                continue

            subplot_cfg.add_column(cfg.ColumnConfig(col_name))
        plot_cfg.add_subplot(subplot_cfg)

    # Plot data
    plotting.plot_csv_data(data_obj, plot_cfg)


def __handle_util_args(args):
    if args.list_headers:
        list_headers(args.input_file)
    elif args.calc_metrics:
        calc_metrics(args.input_file)
    elif args.transform:
        # TODO: add additional necessary arguments
        transform_file(args.input_file)


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
