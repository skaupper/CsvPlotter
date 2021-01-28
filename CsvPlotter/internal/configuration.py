from .util_classes import SampleRange


class PlotConfig(object):
    def __init__(self, input_filename, range_cfg=SampleRange(), output_filename=None):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.range = range_cfg
        self.subplots = [SubplotConfig()]

    def create_empty_subplots(self, subplot_count):
        self.subplots = [SubplotConfig() for _ in range(subplot_count)]

    def add_column_to_subplot(self, column_cfg, subplot_idx=0):
        if subplot_idx >= len(self.subplots):
            raise KeyError(
                f'Given subplot index ({subplot_idx}) does not exist')

        self.subplots[subplot_idx].add_column(column_cfg)

    def __repr__(self):
        return f'PlotConfig{{input_filename={self.input_filename!r}, output_filename={self.output_filename!r}, range={self.range!r}, subplots={self.subplots!r}}}'


class ColumnConfig(object):
    def __init__(self, name=None, label=None, alt_y_axis=False):
        self.name = name
        self.alt_y_axis = alt_y_axis
        self.label = label if label is not None else name

    def __repr__(self):
        return f'ColumnConfig{{name={self.name!r}, label={self.label!r}, alt_y_axis={self.alt_y_axis!r}}}'


class SubplotConfig(object):
    def __init__(self):
        self.columns = []

    def add_column(self, column_cfg):
        self.columns.append(column_cfg)

    def __repr__(self):
        return f'SubplotConfig{{columns={self.columns!r}}}'
