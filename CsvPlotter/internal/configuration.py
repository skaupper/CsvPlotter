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


class ColumnConfig(object):
    def __init__(self, col_name=None, label=None, alt_y_axis=False):
        self.column_name = col_name
        self.alt_y_axis = alt_y_axis
        self.label = label if label is not None else col_name


class SubplotConfig(object):
    def __init__(self):
        self.columns = []

    def add_column(self, column_cfg):
        self.columns.append(column_cfg)
