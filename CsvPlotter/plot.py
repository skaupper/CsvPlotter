#!/usr/bin/env python

import os
import signal
import argparse
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from math import ceil, floor
signal.signal(signal.SIGINT, signal.SIG_DFL)


#
# Data preparation
#

def init_processed_data(header):
    # Init data structure which will hold CSV data in RAM
    global processed_data

    processed_data = {}
    processed_data['header'] = header
    processed_data['col_indices'] = {}
    for i, h in enumerate(header):
        processed_data['col_indices'][h] = i

    processed_data['data'] = [[]]*len(header)
    processed_data['n'] = 0
    processed_data['i'] = 0


def process_row(csv_row):
    # Process a row of CSV data and store them in RAM
    global processed_data

    new_size = 0
    for i, entry in enumerate(csv_row):
        if processed_data['i'] >= processed_data['n']:
            new_size = processed_data['i']
            if new_size == 0:
                new_size = 10000
            processed_data['data'][i] = np.concatenate(
                (processed_data['data'][i], np.full(new_size, None)))
        processed_data['data'][i][processed_data['i']] = int(entry.strip())

    processed_data['n'] += new_size
    processed_data['i'] += 1


def read_csv_headers(filename):
    # Extract the header row of the CSV file
    with open(filename, 'r') as f:
        plots = csv.reader(f, delimiter=',')

        headers = []
        for head in next(plots):
            headers.append(str(head).strip())

        return headers


def read_csv_data(filename, divider, start, end):
    # Read a CSV file and store the relevant rows in RAM
    global processed_data

    print('Extract data from file: %s' % filename)

    CHUNK_SIZE = 65536
    THRESHOLD = 1000000


    last_data_index = -1

    init_processed_data(read_csv_headers(filename))


    with open(filename, 'r') as f:
        plots = csv.reader(f, delimiter=',')
        for i, row in enumerate(plots):
            if i == 0:
                # The header is already read.
                continue

            data_index = i-1

            if data_index >= end and end != -1:
                break

            if data_index % THRESHOLD == 0 and data_index != 0:
                print('%d samples read' % data_index)

            if data_index % divider != 0:
                continue

            if data_index >= start:
                process_row(row)
                last_data_index = data_index

    if last_data_index < 0:
        print('No relevant samples stored!')
        return None

    print('Finished: %d samples read' % processed_data['i'])
    return (start, last_data_index)



#
# Plotting
#

def plot_helper(axis, data_list):
    # Take a list of data points and add them to the given plot axis (resp. its twin axis).
    LINE_STYLE = '.-'

    alt_axis = None
    line_objects = []
    labels = []
    for i, entry in enumerate(data_list):
        x = entry['x']
        data = entry['data']
        label = entry['label']
        alt_y = entry['alt_y']

        if alt_y:
            if alt_axis is None:
                alt_axis = ax.twinx()
            ax = alt_axis
        else:
            ax = axis

        labels.append(label)

        line_objects.append(ax.plot(x, data, 'C'+str(i)+LINE_STYLE)[0])

    axis.legend(line_objects, labels, loc='upper left',
                bbox_to_anchor=(1.08, 1.0))

    return axis, alt_axis


def plot_processed_data(divider, start, end, headers):
    global processed_data

    #
    # Calculate x axis
    #

    if end == -1:
        end = processed_data['i'] * divider
    if start == -1:
        start = 0

    if start % divider != 0:
        start = int(ceil(float(start) / divider) * divider)
    if end % divider != 0:
        end = int(floor(float(end) / divider) * divider)

    x = range(start, end+divider, divider)


    #
    # Helper functions for plotting
    #

    def get_view(arr):
        if len(arr) < (end-start)/divider:
            return None
        return arr[:int((end-start)/divider+1)]

    def get_view_empty():
        return [None]*((end-start)/divider+1)

    def pack_processed_data(label, data=None, alt_y=False):
        if data is None:
            if label not in processed_data['col_indices']:
                data = get_view_empty()
                print('Column "%s" not found!' % label)
            else:
                data = get_view(
                    processed_data['data'][processed_data['col_indices'][label]])
                if data is None:
                    print('Column "%s" has not enough data!' % label)
                    data = get_view_empty()
        return {
            'x': x,
            'data': data,
            'label': label,
            'alt_y': alt_y
        }

    # plot data
    print('Plot data...')

    # create subplots
    fig, axes = plt.subplots(1, sharex=True)
    plt.subplots_adjust(top=0.93, bottom=0.07, left=0.07, right=0.85)

    series = []
    for h in headers:
        series.append(pack_processed_data(h))

    ax, alt_ax = plot_helper(axes, series)

    ax.set(xlabel='Samples')
    ax.grid()

    plt.show()



def run():
    #
    # Parse the input arguments
    #

    def divide_check(v):
        # Only positive integers are allowed as a divider.

        error = True
        try:
            v = int(v)
            error = v < 1
        finally:
            if error:
                raise argparse.ArgumentTypeError('Positive integer expected')
        return v

    def region_check(v):
        # The region of samples to be plotted should be given in the form START:END.
        # Negative values for either of START or END represent the first resp. the last sample (i.e. a value of -1 for END
        # sets END to the index of the last sample).
        # Omitting either of the values will set its value to default (0 for START and -1 for END).

        error = True
        try:
            v = str(v)
            region = v.split(':')
            if len(region) != 2:
                raise
            start = int(region[0]) if len(region[0]) > 0 else 0
            end = int(region[1]) if len(region[1]) > 0 else -1

            if start < 0:
                start = 0
            if end < 0:
                end = -1

            error = False
        finally:
            if error:
                raise argparse.ArgumentTypeError(
                    'Region string of the form \'START:END\' expected')
        return (start, end)


    #
    # Specify the CLI
    #

    parser = argparse.ArgumentParser(description='Processes memory dumps of debug data and plots it')
    parser.add_argument('filename', help='CSV debug data')
    parser.add_argument('headers',  type=str, nargs='+',
                        help='Divides the input data to only take each nth packet', default=1)
    parser.add_argument('-d', '--divide',       type=divide_check,
                        help='Divides the input data to only take each nth packet', default=1)
    parser.add_argument('-r', '--region',       type=region_check,       help='Specifies the desired data range in format \'START:END\' (both inclusive). '
                                                                              'START and END (or both) my be omitted to specify an open range '
                                                                              'e.g. use \'100:\' to plot all data from the 100th sample until the last one.', default=':')
    parser.add_argument('-s', '--headers-only', action='store_true', help='Only print headers without plotting', default=False)

    args = parser.parse_args()
    (start, end) = args.region


    #
    # Invoke the program
    #
    if args.headers_only:
        headers = read_csv_headers(args.filename)
        for h in headers:
            print(h)
    else:
        (start, end) = read_csv_data(args.filename, args.divide, start, end)
        plot_processed_data(args.divide, start, end, args.headers)
