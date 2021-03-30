from .. import csv_handling


def calc_metrics(input_file):
    data_obj = csv_handling.CsvData.from_file(input_file)
    for h in data_obj.headers:
        print('Column "{}"'.format(h))
        print('    Min: {}'.format(min(data_obj.data[h])))
        print('    Max: {}'.format(max(data_obj.data[h])))
        print('    Avg: {}'.format(
            sum(data_obj.data[h][:data_obj.size]) / data_obj.size))
        print()
