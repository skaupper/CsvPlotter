__true_map = ['true', 't', '1', 'y', 'yes']
__false_map = ['false', 'f', '0', 'n', 'no']


def str2bool(s):
    if s.lower() in __true_map:
        return True
    if s.lower() in __false_map:
        return False
    raise ValueError(f'"{s}" is not a valid boolean value!')


class Range(object):
    def __init__(self, start=None, end=None, divider=1):
        self.start = start
        self.end = end
        self.divider = divider

    def __contains__(self, num):
        if type(num) == int and num % self.divider != 0:
            return False
        if self.start is not None and num < self.start:
            return False
        if self.end is not None and num >= self.end:
            return False
        return True

    def __repr__(self):
        return f'Range{{start={self.start!r}, end={self.end!r}, divider={self.divider!r}}}'
