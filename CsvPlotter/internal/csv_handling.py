import numpy as np
import csv

from .utils import str2bool


def read_headers(filename):
    with open(filename, 'r') as f:
        plots = csv.reader(f, delimiter=',')
        return [str(head).strip() for head in next(plots)]


class CsvData(object):
    INITIAL_CAPACITY = 10000

    def __init__(self, headers):
        self.capacity = 0
        self.size = 0
        self.headers = headers

        csv_data = {}
        for h in headers:
            csv_data[h] = np.array([], dtype=np.float32)
        self.data = csv_data

    def __increase_capacity(self, incr):
        self.capacity += incr
        for h in self.headers:
            self.data[h] = np.concatenate(
                (self.data[h], np.full(incr, None, dtype=np.float32)))

    def add_row(self, row):
        if self.size >= self.capacity:
            incr = self.capacity if self.capacity != 0 else self.INITIAL_CAPACITY
            self.__increase_capacity(incr)

        for idx, col in enumerate(row):
            h = self.headers[idx]
            val_str = col.strip()
            val = None

            # Try parsing the given entry
            try:
                val = 1 if str2bool(val_str) else 0
            except ValueError:
                pass
            try:
                val = float(val_str)
                val = int(val_str)
            except ValueError:
                pass

            if val is None:
                print(f'Unsupported value type of "{val_str}"!')
                return

            self.data[h][self.size] = val

        self.size += 1

    def __repr__(self):
        return f'CsvData{{size={self.size!r}, capacity={self.capacity!r}, headers={self.headers!r}, data={self.data!r}}}'

    @classmethod
    def from_file(cls, config):
        print(f'Extract data from file: {config.input_file}')

        PRINT_THRESHOLD = 1000000

        data_obj = cls(read_headers(config.input_file))

        with open(config.input_file, 'r') as f:
            plots = csv.reader(f, delimiter=',')
            for i, row in enumerate(plots):
                if i == 0:
                    # The header is already read.
                    continue

                data_index = i-1
                if data_index % PRINT_THRESHOLD == 0 and data_index != 0:
                    print(f'{data_index} samples read')

                # If the end of the region has reached, exit the loop
                if data_index not in config.range:
                    if config.range.end is not None and data_index >= config.range.end:
                        break
                    else:
                        continue

                data_obj.add_row(row)

        if data_obj.size == 0:
            print('No relevant samples stored!')
        else:
            print(f'Finished: {data_obj.size} samples read')
        return data_obj
