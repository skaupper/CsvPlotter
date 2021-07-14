from .. import csv_handling


def calc_metrics(input_file: str):
    data_obj = csv_handling.CsvData.from_file(input_file)
    for h in data_obj.headers:
        d = data_obj.data[h][:data_obj.size]
        print('Column "{}"'.format(h))
        print('    Min:  {}'.format(min(d)))
        print('    Max:  {}'.format(max(d)))
        print('    Sum:  {}'.format(sum(d)))
        print('    Size: {}'.format(data_obj.size))
        print('    Avg:  {}'.format(sum(d) / data_obj.size))
        print()
