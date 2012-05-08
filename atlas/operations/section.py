#!/usr/bin/env python

import optparse

import pylab

from .. import section


def parse(args):
    parser = optparse.OptionParser()
    parser.add_option('-p', '--plot', help="generate plot",
            default=False, action="store_true")
    parser.add_option('-o', '--output', help="output filename",
            default='plot.png')
    parser.add_option('-s', '--show', help="show",
            default=False, action="store_true")
    return parser.parse_args(args)


def run(args):
    assert len(args) > 2, "Must supply 3 location coordinates: %s" % args
    ml, dv, ap = [float(a) for a in args[:3]]

    options, args = parse(args[3:])

    # get closest section
    cs = section.get_closest_section(ap)

    print cs.index
    if options.plot:
        # plot point on closest section
        sim = cs.get_section_image()
        pylab.imshow(sim)
        ix, iy = cs.frame_stack.convert(ml, dv, 'skull', 'png')
        pylab.scatter(ix, iy)
        fn = options.output

        # TODO turn off all axes, scale to just image, etc...

        pylab.savefig(fn)
        if options.show:
            pylab.show()
