from .samplerange import SampleRange


class PlotConfig(object):
    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.range = SampleRange()
        self.share_x_axis = True
        self.subplots = []

    @classmethod
    def from_obj(cls, cfg_obj):
        def get_or_default(key, default=None, conv=None):
            if key not in cfg_obj or cfg_obj[key] is None:
                return default
            v = cfg_obj[key]
            if conv is not None:
                return conv(v)
            return v

        plot_cfg = cls()
        plot_cfg.input_file = get_or_default('input_file', conv=str)
        plot_cfg.output_file = get_or_default('output_file', conv=str)
        plot_cfg.range.start = get_or_default('range_start', 0, conv=int)
        plot_cfg.range.end = get_or_default('range_end', -1, conv=int)
        plot_cfg.range.divider = get_or_default('divider', 1, conv=int)
        plot_cfg.share_x_axis = get_or_default('share_x_axis', True, conv=bool)

        for p in get_or_default('plots', []):
            plot_cfg.add_subplot(SubplotConfig.from_obj(p))

        return plot_cfg

    def add_subplot(self, subplot_cfg):
        self.subplots.append(subplot_cfg)

    def __repr__(self):
        return f'PlotConfig{{input_file={self.input_file!r}, output_file={self.output_file!r}, range={self.range!r}, subplots={self.subplots!r}}}'


class SubplotConfig(object):
    def __init__(self):
        self.title = None
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self.alt_ylabel = None
        self.columns = []

    @classmethod
    def from_obj(cls, cfg_obj):
        def get_or_default(key, default=None, conv=None):
            if key not in cfg_obj or cfg_obj[key] is None:
                return default
            v = cfg_obj[key]
            if conv is not None:
                return conv(v)
            return v

        subplot_cfg = cls()
        subplot_cfg.title = get_or_default('title', conv=str)
        subplot_cfg.xlabel = get_or_default('xlabel', 'X', conv=str)
        subplot_cfg.ylabel = get_or_default('ylabel', 'Y', conv=str)
        subplot_cfg.alt_ylabel = get_or_default('alt_ylabel', conv=str)

        for c in get_or_default('columns', []):
            subplot_cfg.add_column(ColumnConfig.from_obj(c))

        return subplot_cfg

    def add_column(self, column_cfg):
        self.columns.append(column_cfg)

    def __repr__(self):
        return f'SubplotConfig{{columns={self.columns!r}}}'


class ColumnConfig(object):
    def __init__(self, name=None, label=None, alt_y_axis=False):
        self.name = name
        self.alt_y_axis = alt_y_axis
        self.label = label if label is not None else name

    @classmethod
    def from_obj(cls, cfg_obj):
        def get_or_default(key, default=None, conv=None):
            if key not in cfg_obj or cfg_obj[key] is None:
                return default
            v = cfg_obj[key]
            if conv is not None:
                return conv(v)
            return v

        column_cfg = cls()
        column_cfg.name = get_or_default('name', conv=str)
        column_cfg.label = get_or_default('label', conv=str)
        column_cfg.alt_y_axis = get_or_default('alt_y_axis', False, conv=bool)

        return column_cfg

    def __repr__(self):
        return f'ColumnConfig{{name={self.name!r}, label={self.label!r}, alt_y_axis={self.alt_y_axis!r}}}'
