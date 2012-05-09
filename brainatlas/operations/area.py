#!/usr/bin/env python

import optparse

from .. import section


def parse(args):
    parser = optparse.OptionParser()
    parser.add_option('-a', '--areas', help="areas to parse",
        default='V2L AuD Au1 AuV PRh V1B V1M TeA Ect')
    return parser.parse_args(args)


def run(args):
    # pyatlas area <location>
    assert len(args) > 2, "Must supply 3 location coordinates: %s" % args
    ml, dv, ap = [float(a) for a in args[:3]]

    options, args = parse(args[3:])

    areas = options.areas.split()
    assert len(areas) > 0, "No areas supplied"

    # get closest section
    cs = section.get_closest_section(ap, areas=areas)

    # lookup area
    area = cs.get_area_for_location(ml, dv, 'skull')

    try:
        if len(area):
            print area[0]
    except:
        print area
