#!/usr/bin/env python


import sys

import brainatlas
import brainatlas.operations


# I want this to
#  - plot a location on the closest section
#       pyatlas section <location>
#  - get perimeter points for an area
#       pyatlas points <area>
#  - look up the area which contains a location
#       pyatlas area <location>
#  - plot a location on a flattened cylindrical cortex
#       pyatlas cortex <location>
#
# usage:
#   pyatlas <operation> <args/options>
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: pyatlas <operation> [args/options]"
        sys.exit(1)
    brainatlas.operations.run(sys.argv[1], sys.argv[2:])
