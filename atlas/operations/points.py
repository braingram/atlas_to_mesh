#!/usr/bin/env python

import optparse
import os

import numpy

from .. import construct
from .. import section


def parse(args):
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output', help="output file/directory",
            default=None)
    parser.add_option('-m', '--mesh',
            help="generate mesh (.asc) files in output directory",
            default=False, action="store_true")
    parser.add_option('-s', '--sections',
            help="section indices to parse (space separated)",
            default=None)
    return parser.parse_args(args)


def run(args):
    options, args = parse(args)

    assert len(args) > 0, "Must supply at least 1 area"
    areas = args

    if options.sections is None:
        options.sections = [i for i in range(12, 162) \
                if not (i in [22, 47, 76, 144, 148])]

    sections = [section.load(si, areas=areas) for si in options.sections]
    pts = {}
    for area in areas:
        pts[area] = construct.get_points(area, sections=sections)

    if options.mesh:
        outdir = options.output
        if outdir is None:
            outdir = 'meshes'
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        for area in areas:
            fn = os.path.join(outdir, area) + '.asc'
            numpy.savetxt(fn, pts[area])
    else:
        for area in areas:
            for pt in pts[area]:
                print pt
