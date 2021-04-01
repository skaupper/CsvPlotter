from typing import Optional


__true_map = ['true', 't', '1', 'y', 'yes']
__false_map = ['false', 'f', '0', 'n', 'no']


def str2bool(s: str) -> bool:
    if s.lower() in __true_map:
        return True
    if s.lower() in __false_map:
        return False
    raise ValueError(f'"{s}" is not a valid boolean value!')


class Range(object):
    start: Optional[int]
    end: Optional[int]
    divider: int

    def __init__(self, start: Optional[int] = None,
                 end: Optional[int] = None,
                 divider: int = 1):
        self.start = start
        self.end = end
        self.divider = divider

    def __contains__(self, num: int) -> bool:
        if type(num) == int and num % self.divider != 0:
            return False
        if self.start is not None and num < self.start:
            return False
        if self.end is not None and num >= self.end:
            return False
        return True

    def __repr__(self) -> str:
        return f'Range{{start={self.start!r}, end={self.end!r}, divider={self.divider!r}}}'
