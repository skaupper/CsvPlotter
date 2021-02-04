import signal
import matplotlib.pyplot as plt


#
# Private helper functions
#

def __plot_subplot(data_obj, config, subplot, axis):
    LINE_STYLE = '.-'

    line_objects = []
    labels = []

    x = config.range.get_index_list(data_obj.size)

    for i, col in enumerate(subplot.columns):
        if col.alt_y_axis:
            # TODO
            continue

        y = data_obj.data[col.name][:data_obj.size]

        labels.append(col.name if col.label is None else col.label)
        line_objects.append(axis.plot(
            x, y, f'C{i}{LINE_STYLE}')[0]
        )

    axis.legend(line_objects, labels, loc='upper left')
    axis.set_xlabel(subplot.xlabel)
    axis.set_ylabel(subplot.ylabel)
    if subplot.title is not None:
        axis.set_title(subplot.title)
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
