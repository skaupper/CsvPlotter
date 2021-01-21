import matplotlib.pyplot as plt
from math import ceil, floor


#
# Private helper function for preprocessing and plotting data
#


def __prepare_data_set(data_obj, col_id, range_cfg, label=None):
    if label is None:
        label = col_id

    # col_idx = __resolve_column_index(data_obj, col_id)
    # if col_idx is None:
    #     raise KeyError(f'No column "{col_id}" exists!')

    return {
        'x': __generate_x_axis(range_cfg),
        'y': __get_data_view(data_obj['data'][col_id], range_cfg),
        'label': label
    }


def __generate_all_data_series(data_obj, config):
    all_series = []
    for h in headers:
        try:
            all_series.append(__prepare_data_set(data_obj, h, range_cfg))
        except KeyError as e:
            print(e)
    return all_series


def __plot_all_series(axis, all_series):
    # Take a list of data points and add them to the given plot axis (resp. its twin axis).
    LINE_STYLE = '.-'

    line_objects = []
    labels = []

    for i, series in enumerate(all_series):
        labels.append(series['label'])
        line_objects.append(
            axis.plot(series['x'], series['y'], 'C'+str(i)+LINE_STYLE)[0])

    axis.legend(line_objects, labels, loc='upper left')


def __plot(all_series):
    _, axis = plt.subplots(1, sharex=True)

    __plot_all_series(axis, all_series)
    axis.set(xlabel='Samples')
    axis.grid()

    print('Plot data...')
    plt.show()


#
# Public plotting function
#

def plot_csv_data(data_obj, config):

    # TODO: implement plotting using the new object and config layouts

    print('Subplot contents:')
    for subplot in config.subplots:
        print(f'{len(subplot.columns)}')

    # all_series = __generate_all_data_series(data_obj, config)
    # __plot(all_series)
