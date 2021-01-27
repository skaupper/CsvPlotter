from math import ceil, floor


class SampleRange(object):
    def __init__(self, start=0, end=-1, divider=1):
        self.start = start
        self.end = end
        self.divider = divider

    def __assert_validity(self):
        if self.start < 0 or self.end < 0:
            raise ValueError('The object does not represent a valid range '
                             f'({self.start}-{self.end})!')
        if self.divider <= 0:
            raise ValueError('The divider value must be positive but it '
                             f'was {self.divider}!')

    def update_range(self, start=None, end=None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

    def correct_values(self):
        self.__assert_validity()

        # Round start up to the next integer multiple of divider, if necessary
        if self.start % self.divider != 0:
            self.start = int(ceil(float(self.start) / self.divider)
                             * self.divider)

        # Round end down to the latest integer multiple of divider, if necessary
        if self.end % self.divider != 0:
            self.end = int(floor(float(self.end) / self.divider)
                           * self.divider)

    def get_range(self):
        self.__assert_validity()
        return range(self.start, self.end+self.divider, self.divider)

    def apply_to_data(self, data):
        if len(data) < (self.end-self.start)/self.divider:
            return None
        return data[:int((self.end-self.start)/self.divider+1)]

    def __contains__(self, num):
        if num % self.divider != 0:
            return False

        if num < self.start or (num >= self.end and self.end != -1):
            return False

        return True
