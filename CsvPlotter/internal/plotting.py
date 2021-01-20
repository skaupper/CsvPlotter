import matplotlib.pyplot as plt
from math import ceil, floor


#
# Private helper function for preprocessing and plotting data
#

def __generate_x_axis(range_cfg):
    start = range_cfg['start']
    end = range_cfg['end']
    divider = range_cfg['divider']

    if start == -1 or end == -1:
        raise ValueError(f'The given region values ({start}:{end}) are not valid!')

    # Round start up to the next integer multiple of divider, if necessary
    if start % divider != 0:
        start = int(ceil(float(start) / divider) * divider)

    # Round end down to the latest integer multiple of divider, if necessary
    if end % divider != 0:
        end = int(floor(float(end) / divider) * divider)

    # Generate the value for the X-Axis
    return range(start, end+divider, divider)


def __resolve_column_index(data_obj, col_id):
    # The column ID specified by the user is translated to a CSV column either as:
    # 1) The name of a column header, if any such column exists.
    # 2) As column index otherwise, if possible.
    col_idx = None
    try:
        col_idx = int(col_id)
    except ValueError:
        pass
    try:
        col_idx = data_obj['header'].index(col_id)
    except ValueError:
        pass
    return col_idx


def __get_data_view(data, range_cfg):
    start = range_cfg['start']
    end = range_cfg['end']
    divider = range_cfg['divider']

    if len(data) < (end-start)/divider:
        return None
    return data[:int((end-start)/divider+1)]


def __prepare_data_set(data_obj, x, col_id, range_cfg, label=None):
    if label is None:
        label = col_id

    # col_idx = __resolve_column_index(data_obj, col_id)
    # if col_idx is None:
    #     raise KeyError(f'No column "{col_id}" exists!')

    return {
        'x': x,
        'y': __get_data_view(data_obj['data'][col_id], range_cfg),
        'label': label
    }


def __generate_all_data_series(data_obj, x, range_cfg, headers):
    all_series = []
    for h in headers:
        try:
            all_series.append(__prepare_data_set(data_obj, x, h, range_cfg))
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
        line_objects.append(axis.plot(series['x'], series['y'], 'C'+str(i)+LINE_STYLE)[0])

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

def plot_csv_data(data_obj, headers, start, end, divider):
    range_cfg = {
        'start': start,
        'end': end,
        'divider': divider
    }

    x = __generate_x_axis(range_cfg)
    all_series = __generate_all_data_series(data_obj, x, range_cfg, headers)
    __plot(all_series)
