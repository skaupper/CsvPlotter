from math import log10, ceil

from .. import csv_handling


def list_headers(input_file: str):
    headers = csv_handling.read_headers(input_file)
    print(f'Column headers found: {len(headers)}')
    idx_width = ceil(log10(len(headers)))
    for i, header in enumerate(headers):
        print(f'  {i:{idx_width}} : {header}')
