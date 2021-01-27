import matplotlib.pyplot as plt


#
# Private helper functions
#

def __plot_subplot(data_obj, config, subplot, axis):
    LINE_STYLE = '.-'

    line_objects = []
    labels = []

    x = config.range.get_range()

    for i, col in enumerate(subplot.columns):
        y = config.range.apply_to_data(data_obj.data[col.column_name])

        labels.append(col.label)
        line_objects.append(axis.plot(
            x, y, f'C{i}{LINE_STYLE}')[0]
        )

    axis.legend(line_objects, labels, loc='upper left')
    axis.set(xlabel='Samples')
    axis.grid()


#
# Public plotting function
#

def plot_csv_data(data_obj, config):

    # Prepare subplots
    _, axes = plt.subplots(len(config.subplots), sharex=True)
    if type(axes) != type([]):
        axes = [axes]

    for i, subplot in enumerate(config.subplots):
        __plot_subplot(data_obj, config, subplot, axes[i])

    if config.output_filename is None:
        print('Plot data...')
        plt.show()
    else:
        print(f'Plot data to output file {config.output_filename}...')
        plt.savefig(config.output_filename)
