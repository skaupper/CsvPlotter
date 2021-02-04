import signal
from math import ceil, floor
import matplotlib.pyplot as plt


#
# Private helper functions
#

def __get_index_list(rng, nr_of_indices=None):
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


def __plot_subplot(data_obj, config, subplot, axis):
    LINE_STYLE = '.-'

    line_objects = []
    labels = []

    x = __get_index_list(config.range, data_obj.size)
    alt_axis = None

    for i, col in enumerate(subplot.columns):
        # Determine the correct axis to plot to
        if not col.alt_y_axis:
            curr_axis = axis
        else:
            if alt_axis is None:
                alt_axis = axis.twinx()
            curr_axis = alt_axis

        y = data_obj.data[col.name][:data_obj.size]

        # Plot data and add labels
        labels.append(col.name if col.label is None else col.label)
        line_objects.append(curr_axis.plot(
            x, y, f'C{i}{LINE_STYLE}')[0]
        )

    # Do general axes configuration like legends, labels,
    axis.legend(line_objects, labels, loc='upper left')
    axis.set_xlabel(subplot.xlabel)
    axis.set_ylabel(subplot.ylabel)
    axis.set_ylim(subplot.ylim.start, subplot.ylim.end)
    axis.set_title(subplot.title)

    if alt_axis is not None:
        alt_axis.set_ylabel(subplot.alt_ylabel)
        alt_axis.set_ylim(subplot.alt_ylim.start, subplot.alt_ylim.end)
    axis.grid()


#
# Public plotting function
#

def plot_csv_data(data_obj, config):
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
