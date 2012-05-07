#!/usr/bin/env python

import optparse

from .. import section


def parse(args):
    parser = optparse.OptionParser()
    parser.add_option('-a', '--areas', help="areas to plot",
            default='V2L AuD Au1 AuV PRh V1B V1M Ect TeA')
    parser.add_option('-o', '--output', help="output filename",
            default="cortex.png")
    parser.add_option('-p', '--plot', help="generate plot",
            default=False, action="store_true")
    parser.add_option('-x', '--cylinderx',
            help="cylinder center ml coordinate (+right)",
            default=0, type="float")
    parser.add_option('-y', '--cylindery',
            help="cylinder center dv coordinate (+dorsal)",
            default=6, type="float")
    return parser.parse_args(args)


def run(args):
    options, args = parse(args)

    assert len(args) == 3, "Must supply 3 location coordinates: %s" % args
    areas = options.areas.split()
    assert len(areas) > 0, "No areas supplied"

    ml, dv, ap = [float(a) for a in args]

    # get closest section
    cs = section.get_closest_section(ap, areas=areas)

    # project on cortex
    raise NotImplementedError
