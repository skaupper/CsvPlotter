from typing import Any, Callable, Dict, List, Optional
from .utils import Range


def _get_or_default(
    cfg_obj: Dict[str, Optional[str]],
    key: str,
    default: Any = None,
    conv: Optional[Callable[[str], Any]] = None,
) -> Any:
    if key not in cfg_obj or cfg_obj[key] is None:
        return default

    v = cfg_obj[key]
    assert v is not None

    if conv is not None:
        return conv(v)
    return v


def _assign_range(rng: Range, obj: List[int]):
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
    input_file: Optional[str]
    output_file: Optional[str]
    range: Range
    share_x_axis: bool
    subplots: List["SubplotConfig"]

    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.range = Range()
        self.share_x_axis = True
        self.subplots = []

    @classmethod
    def from_obj(
        cls,
        # TODO: maybe the type can be specified more concretely?
        cfg_obj: Dict[str, Any],
    ):

        plot_cfg = cls()
        plot_cfg.input_file = _get_or_default(cfg_obj, "input_file", conv=str)
        plot_cfg.output_file = _get_or_default(cfg_obj, "output_file", conv=str)
        plot_cfg.range.divider = _get_or_default(cfg_obj, "divider", 1, conv=int)
        plot_cfg.share_x_axis = _get_or_default(
            cfg_obj, "share_x_axis", True, conv=bool
        )

        _assign_range(
            plot_cfg.range, _get_or_default(cfg_obj, "xlim", [None, None], conv=list)
        )

        for p in _get_or_default(cfg_obj, "plots", []):
            plot_cfg.add_subplot(SubplotConfig.from_obj(p))

        return plot_cfg

    def add_subplot(self, subplot_cfg: "SubplotConfig"):
        self.subplots.append(subplot_cfg)

    def __repr__(self):
        return f"PlotConfig{{input_file={self.input_file!r}, output_file={self.output_file!r}, range={self.range!r}, subplots={self.subplots!r}}}"


class SubplotConfig(object):
    title: Optional[str]
    xlabel: str
    ylabel: str
    ylim: Range
    alt_ylim: Range
    alt_ylabel: Optional[str]
    columns: List["ColumnConfig"]

    def __init__(self):
        self.title = None
        self.xlabel = "X"
        self.ylabel = "Y"
        self.xvalues = None
        self.ylim = Range()
        self.alt_ylim = Range()
        self.alt_ylabel = None
        self.columns = []

    @classmethod
    def from_obj(cls, cfg_obj: Dict[str, Optional[str]]):
        subplot_cfg = cls()
        subplot_cfg.title = _get_or_default(cfg_obj, "title", conv=str)
        subplot_cfg.xlabel = _get_or_default(cfg_obj, "xlabel", "X", conv=str)
        subplot_cfg.ylabel = _get_or_default(cfg_obj, "ylabel", "Y", conv=str)
        subplot_cfg.xvalues = _get_or_default(cfg_obj, "xvalues", conv=str)
        subplot_cfg.alt_ylabel = _get_or_default(cfg_obj, "alt_ylabel", conv=str)

        _assign_range(
            subplot_cfg.ylim, _get_or_default(cfg_obj, "ylim", [None, None], conv=list)
        )
        _assign_range(
            subplot_cfg.alt_ylim,
            _get_or_default(cfg_obj, "alt_ylim", [None, None], conv=list),
        )

        for c in _get_or_default(cfg_obj, "columns", []):
            subplot_cfg.add_column(ColumnConfig.from_obj(c))

        return subplot_cfg

    def add_column(self, column_cfg: "ColumnConfig"):
        self.columns.append(column_cfg)

    def __repr__(self):
        return f"SubplotConfig{{columns={self.columns!r}}}"


class ColumnConfig(object):
    name: str
    label: Optional[str]
    alt_y_axis: bool

    def __init__(
        self, name: str, label: Optional[str] = None, alt_y_axis: bool = False
    ):
        self.name = name
        self.alt_y_axis = alt_y_axis
        self.label = label if label is not None else name

    @classmethod
    def from_obj(cls, cfg_obj: Dict[str, Optional[str]]):
        name = cfg_obj["name"]
        assert name is not None

        column_cfg = cls(name)
        column_cfg.label = _get_or_default(cfg_obj, "label", conv=str)
        column_cfg.alt_y_axis = _get_or_default(cfg_obj, "alt_y_axis", False, conv=bool)

        return column_cfg

    def __repr__(self):
        return f"ColumnConfig{{name={self.name!r}, label={self.label!r}, alt_y_axis={self.alt_y_axis!r}}}"
