from CsvPlotter.internal.utils import Range
from typing import List, Optional
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from CsvPlotter.internal.configuration import PlotConfig, SubplotConfig
from CsvPlotter.internal.csv_handling import CsvData
import signal
from math import ceil
import matplotlib.pyplot as plt


#
# Private helper functions
#

def __get_index_list(rng: Range, nr_of_indices: Optional[int] = None) -> range:
    start = rng.start if rng.start is not None else 0

    corr_start_idx = int(ceil(float(start) / rng.divider) * rng.divider)
    if rng.end is not None:
        corr_end_idx = int(ceil(float(rng.end) / rng.divider) * rng.divider)
    elif nr_of_indices is not None:
        corr_end_idx = corr_start_idx+rng.divider*nr_of_indices
    else:
        raise ValueError(f'Could not determine the end of the range "{rng.start}:{rng.end}", '
                         'since "nr_of_indices" is not given either.')
    return range(corr_start_idx, corr_end_idx, rng.divider)


def __plot_subplot(data_obj: CsvData, config: PlotConfig, subplot: SubplotConfig, axis: Axes):
    LINE_STYLE = '.-'

    line_objects: List[Line2D] = []
    labels: List[str] = []

    x = __get_index_list(config.range, data_obj.size)
    alt_axis: Optional[Axes] = None
    curr_axis: Axes

    for i, col in enumerate(subplot.columns):
        # Determine the correct axis to plot to
        if not col.alt_y_axis:
            curr_axis = axis
        else:
            if alt_axis is None:
                alt_axis = axis.twinx()
            assert alt_axis is not None
            curr_axis = alt_axis

        y = data_obj.data[col.name][:data_obj.size]

        # Plot data and add labels
        labels.append(col.name if col.label is None else col.label)
        line_objects.append(curr_axis.plot(
            x, y, f'C{i}{LINE_STYLE}')[0]
        )

    # Do general axes configuration like legends, labels,
    axis.set_xlabel(subplot.xlabel)
    axis.set_ylabel(subplot.ylabel)
    axis.set_ylim(subplot.ylim.start, subplot.ylim.end)
    axis.set_title(subplot.title)

    legend = axis.legend(line_objects, labels, loc='upper left')
    if alt_axis is not None:
        legend.remove()
        alt_axis.add_artist(legend)
        alt_axis.set_ylabel(subplot.alt_ylabel)
        alt_axis.set_ylim(subplot.alt_ylim.start, subplot.alt_ylim.end)
    axis.grid()


#
# Public plotting function
#

def plot_csv_data(data_obj: CsvData, config: PlotConfig):
    # Make sure Ctrl+C in the terminal closes the plot
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Prepare subplots
    _, axes = plt.subplots(len(config.subplots), sharex=config.share_x_axis)
    try:
        axes[0]
    except:
        axes = [axes]

    for i, subplot in enumerate(config.subplots):
        __plot_subplot(data_obj, config, subplot, axes[i])

    plt.tight_layout()

    if config.output_file is None:
        print('Plot data...')
        plt.show()
    else:
        print(f'Plot data to output file {config.output_file}...')
        plt.savefig(config.output_file)
