#!/usr/bin/env python

import optparse
import os
import cPickle as pickle

import numpy

from .. import construct
from .. import section


def parse(args):
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output', help="output directory",
            default=None)
    parser.add_option('-m', '--mesh',
            help="generate mesh (.asc) files in output directory",
            default=False, action="store_true")
    parser.add_option('-s', '--sections',
            help="section indices to parse (space separated)",
            default=None)
    parser.add_option('-p', '--pickle',
            help="create a pickle file (named this) with the points",
            default=None)
    return parser.parse_args(args)


def run(args):
    options, args = parse(args)

    if len(args) == 0:
        args = section.default_areas
    areas = args

    if options.sections is None:
        options.sections = construct.default_indices

    sections = [section.load(si, areas=areas) for si in options.sections]
    pts = construct.get_points(areas, sections=sections)

    # pickle points?
    if options.pickle is not None:
        fn = options.pickle
        if options.output is not None:
            if not os.path.exists(options.output):
                os.makedirs(options.output)
            fn = os.path.join(options.output, fn)
        with open(fn, 'w') as F:
            pickle.dump(pts, F)

    # make mesh?
    if options.mesh:
        outdir = options.output
        if outdir is None:
            outdir = 'meshes'
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        for area in areas:
            fn = os.path.join(outdir, area) + '.asc'
            numpy.savetxt(fn, pts[area])

    # or else spit out points
    if (not options.mesh) and (options.pickle is None):
        for area in areas:
            for pt in pts[area]:
                print pt
