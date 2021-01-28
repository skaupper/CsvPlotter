from math import ceil


class SampleRange(object):
    def __init__(self, start=0, end=-1, divider=1):
        self.start = start
        self.end = end
        self.divider = divider

    def get_index_list(self, nr_of_indices=None):
        corr_start_idx = int(ceil(float(self.start) / self.divider)
                             * self.divider)
        if self.end != -1:
            corr_end_idx = int(ceil(float(self.end) / self.divider)
                               * self.divider)
        elif nr_of_indices is not None:
            corr_end_idx = corr_start_idx+self.divider*nr_of_indices
        else:
            raise ValueError(f'Could not determine the end of the range "{self.start}:{self.end}", '
                             'since "nr_of_indices" is not given either.')
        return range(corr_start_idx, corr_end_idx, self.divider)

    def __contains__(self, num):
        if num % self.divider != 0:
            return False
        if num < self.start or (num >= self.end and self.end != -1):
            return False
        return True

    def __repr__(self):
        return f'SampleRange{{start={self.start!r}, end={self.end!r}, divider={self.divider!r}}}'
