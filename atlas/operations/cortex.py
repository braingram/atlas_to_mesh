#!/usr/bin/env python

import optparse
import cPickle as pickle

import numpy
import pylab

from .. import construct
from .. import cylinder
#from .. import section


def parse(args):
    parser = optparse.OptionParser()
    parser.add_option('-a', '--areas', help="areas to plot",
            default='V2L AuD Au1 AuV PRh V1B V1M Ect TeA')
    parser.add_option('-A', '--areapts', help="pickled area points",
            default=None)
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
    parser.add_option('-s', '--show', help="show",
            default=False, action="store_true")
    return parser.parse_args(args)


def run(args):
    #pyatlas cortex <location> areas
    assert len(args) > 2, "Must supply 3 location coordinates: %s" % args
    ml, dv, ap = [float(a) for a in args[:3]]

    options, args = parse(args[3:])

    areas = options.areas.split()
    #assert len(areas) > 0, "No areas supplied"

    # project point into cylinder
    ct, cr = cylinder.project(ml, dv, options.cylinderx, options.cylindery)
    cy = ap
    print ct, cr, cy

    # project on cortex
    if options.plot:
        # plot areas
        if len(areas):
            # try to load area points
            if options.areapts is not None:
                try:
                    apts = pickle.load(open(options.areapts, 'r'))
                except:
                    print >> "failed to load area points from: %s" % \
                            options.areapts
                    options.areapts = None
            if options.areapts is None:
                apts = construct.get_points(areas)
            for area in areas:
                pts = numpy.array(apts[area])
                if ml > 0:
                    pts = pts[pts[:, 0] > 0]
                else:
                    pts = pts[pts[:, 0] < 0]
                cylinder.plot_area_points(pts, \
                        options.cylinderx, options.cylindery, \
                        label=area, alpha=0.1)

        # plot location
        pylab.scatter(cy, ct)

        if len(areas):
            pylab.legend()
        fn = options.output

        pylab.savefig(fn)
        if options.show:
            pylab.show()
