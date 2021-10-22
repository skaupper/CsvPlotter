#!/usr/bin/env python

#
# This file is for debug purposes only and should not be called by any user!
#

if __name__ == "__main__":
    import sys
    from . import entrypoints

    module = sys.argv[1]
    del sys.argv[1]

    if module == "transform":
        entrypoints.transform()
    elif module == "plot":
        entrypoints.plot()
    elif module == "util":
        entrypoints.util()
