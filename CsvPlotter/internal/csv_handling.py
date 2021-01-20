import numpy as np
import csv



def __init_data_object(headers):
    csv_data = {}

    for h in headers:
        csv_data[h] = np.array([], dtype=np.int32)

    return {
        'capacity': 0,
        'size': 0,
        'header': headers,
        'data': csv_data
    }

def __process_row(data_obj, csv_row):

    # If the next row would overflow the internal buffer, double its capacity before inserting the data
    increase_by = None
    if data_obj['size'] >= data_obj['capacity']:
        increase_by = data_obj['size']
        if increase_by == 0:
            increase_by = 10000
        data_obj['capacity'] += increase_by
        resize = True
    else:
        resize = False

    # Resize data arrays if needed and insert row data
    for col_idx, col in enumerate(csv_row):
        col_header = data_obj['header'][col_idx]

        if resize:
            data_obj['data'][col_header] = np.concatenate((data_obj['data'][col_header], np.full(increase_by, None)))

        col_data = data_obj['data'][col_header]
        col_data[data_obj['size']] = int(col.strip())

    # One entry has been added to each column
    data_obj['size'] += 1



def read_headers(filename):
    with open(filename, 'r') as f:
        plots = csv.reader(f, delimiter=',')
        return [str(head).strip() for head in next(plots)]


def read_data(filename, divider=1, start=0, end=-1):
    print(f'Extract data from file: {filename}')

    PRINT_THRESHOLD = 1000000

    headers = read_headers(filename)
    data_obj = __init_data_object(headers)
    last_data_index = -1


    with open(filename, 'r') as f:
        plots = csv.reader(f, delimiter=',')
        for i, row in enumerate(plots):
            if i == 0:
                # The header is already read.
                continue

            data_index = i-1

            if data_index % PRINT_THRESHOLD == 0 and data_index != 0:
                print(f'{data_index} samples read')


            # If the end of the region has reached, exit the loop
            if data_index >= end and end != -1:
                break

            # Skip rows until the desired region starts
            if data_index < start:
                continue

            # Skip all rows whose indices are not a multiple of the divider
            if data_index % divider != 0:
                continue

            __process_row(data_obj, row)
            last_data_index = data_index


    if data_obj['size'] == 0:
        print('No relevant samples stored!')
        return (data_obj, -1, -1)

    print(f'Finished: {data_obj["size"]} samples read')
    return (data_obj, start, last_data_index)
