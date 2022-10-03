from typing import Callable, Dict, List, Optional, Union
from CsvPlotter.internal.configuration import PlotConfig
import numpy as np
import csv

from .utils import dir2int, str2bool, Range


def read_headers(filename: str) -> List[str]:
    with open(filename, "r") as f:
        plots = csv.reader(f, delimiter=",")
        return [str(head).strip() for head in next(plots)]


class CsvData(object):
    INITIAL_CAPACITY = 10000

    capacity: int
    size: int
    headers: List[str]
    data: Dict[str, "np.ndarray[Optional[np.float32]]"]

    def __init__(self, headers: List[str]):
        self.capacity = 0
        self.size = 0
        self.headers = headers

        csv_data = {}
        for h in headers:
            csv_data[h] = np.array([], dtype=np.float32)  # type: ignore
        self.data = csv_data

    def __increase_capacity(self, incr: int):
        self.capacity += incr
        for h in self.headers:
            self.data[h] = np.concatenate(  # type: ignore
                (self.data[h], np.full(incr, None, dtype=np.float32))  # type: ignore
            )

    def add_row(self, row: List[str]):
        if self.size >= self.capacity:
            incr = self.capacity if self.capacity != 0 else self.INITIAL_CAPACITY
            self.__increase_capacity(incr)

        for idx, col in enumerate(row):
            h = self.headers[idx]
            val_str = col.strip()
            val = None

            # Try parsing the given entry
            if len(val_str) > 0:
                KNOWN_VALUE_PARSERS: list[Callable[[str], Union[int, float]]] = [
                    dir2int,
                    lambda s: 1 if str2bool(s) else 0,
                ]

                for parser in KNOWN_VALUE_PARSERS:
                    try:
                        val = parser(val_str)
                    except ValueError:
                        pass
                try:
                    val = float(val_str)
                    val = int(val_str)
                except ValueError:
                    pass

                if val is None:
                    print(f'Unsupported value type of "{val_str}" {self.size}!')
                    return

            self.data[h][self.size] = val

        self.size += 1

    def __repr__(self) -> str:
        return f"CsvData{{size={self.size!r}, capacity={self.capacity!r}, headers={self.headers!r}, data={self.data!r}}}"

    @classmethod
    def from_config(cls, config: PlotConfig) -> "CsvData":
        assert config.input_file is not None
        return cls.from_file(config.input_file, config.range)

    @classmethod
    def from_file(cls, input_file: str, sample_range: Range = Range()) -> "CsvData":
        print(f"Extract data from file: {input_file}")

        PRINT_THRESHOLD = 1000000

        class DataObjFunctor:
            data_obj: Optional[CsvData] = None

            def __call__(
                self, i: int, sample_range: Range, row: List[str]
            ) -> Optional[bool]:
                if i == 0:
                    self.data_obj = cls([str(head).strip() for head in row])
                    return

                data_index = i - 1
                if data_index % PRINT_THRESHOLD == 0 and data_index != 0:
                    print(f"{data_index} samples read")

                # If the end of the region has reached, exit the loop
                if data_index not in sample_range:
                    if sample_range.end is not None and data_index >= sample_range.end:
                        return True
                    else:
                        return

                assert self.data_obj is not None
                self.data_obj.add_row(row)

        functor = DataObjFunctor()
        cls.iterate_over_lines(input_file, sample_range, functor)

        data_obj = functor.data_obj
        assert data_obj is not None
        if data_obj.size == 0:
            print("No relevant samples stored!")
        else:
            print(f"Finished: {data_obj.size} samples read")
        return data_obj

    @classmethod
    def iterate_over_lines(
        cls,
        input_file: str,
        sample_range: Range,
        handler: Callable[[int, Range, List[str]], Optional[bool]],
    ):
        with open(input_file, "r") as f:
            reader = csv.reader(f, delimiter=",")
            for i, row in enumerate(reader):
                if handler is not None:
                    exit_loop = handler(i, sample_range, row)
                    if exit_loop:
                        break
