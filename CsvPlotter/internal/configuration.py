from .utils import Range


def _get_or_default(cfg_obj, key, default=None, conv=None):
    if key not in cfg_obj or cfg_obj[key] is None:
        return default
    v = cfg_obj[key]
    if conv is not None:
        return conv(v)
    return v


def _assign_range(rng, obj):
    if len(obj) == 0:
        rng.start = None
        rng.end = None
    elif len(obj) == 1:
        rng.start = obj[0]
        rng.end = None
    else:
        rng.start = obj[0]
        rng.end = obj[1]


class PlotConfig(object):
    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.range = Range()
        self.share_x_axis = True
        self.subplots = []

    @classmethod
    def from_obj(cls, cfg_obj):

        plot_cfg = cls()
        plot_cfg.input_file = _get_or_default(cfg_obj, 'input_file', conv=str)
        plot_cfg.output_file = _get_or_default(cfg_obj, 'output_file',
                                               conv=str)
        plot_cfg.range.divider = _get_or_default(cfg_obj, 'divider',
                                                 1, conv=int)
        plot_cfg.share_x_axis = _get_or_default(cfg_obj, 'share_x_axis',
                                                True, conv=bool)

        _assign_range(plot_cfg.range, _get_or_default(cfg_obj, 'xlim', [None, None],
                                                      conv=list))

        for p in _get_or_default(cfg_obj, 'plots', []):
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
        self.ylim = Range()
        self.alt_ylim = Range()
        self.alt_ylabel = None
        self.columns = []

    @classmethod
    def from_obj(cls, cfg_obj):
        subplot_cfg = cls()
        subplot_cfg.title = _get_or_default(cfg_obj, 'title', conv=str)
        subplot_cfg.xlabel = _get_or_default(cfg_obj, 'xlabel', 'X', conv=str)
        subplot_cfg.ylabel = _get_or_default(cfg_obj, 'ylabel', 'Y', conv=str)
        subplot_cfg.alt_ylabel = _get_or_default(cfg_obj, 'alt_ylabel',
                                                 conv=str)

        _assign_range(subplot_cfg.ylim, _get_or_default(cfg_obj, 'ylim', [None, None],
                                                        conv=list))
        _assign_range(subplot_cfg.alt_ylim, _get_or_default(cfg_obj, 'alt_ylim', [None, None],
                                                            conv=list))

        for c in _get_or_default(cfg_obj, 'columns', []):
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
        column_cfg = cls()
        column_cfg.name = _get_or_default(cfg_obj, 'name', conv=str)
        column_cfg.label = _get_or_default(cfg_obj, 'label', conv=str)
        column_cfg.alt_y_axis = _get_or_default(cfg_obj, 'alt_y_axis', False,
                                                conv=bool)

        return column_cfg

    def __repr__(self):
        return f'ColumnConfig{{name={self.name!r}, label={self.label!r}, alt_y_axis={self.alt_y_axis!r}}}'
