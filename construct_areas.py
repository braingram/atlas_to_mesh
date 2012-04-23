#!/usr/bin/env python

import sys

import pylab

import section
#import points


def construct_areas(sindexes, areas, epsdir='eps/', tmpdir='tmp/', \
        ptsdir='pts/'):
    sections = [section.load(si, areas=areas, indir=epsdir, tmpdir=tmpdir) \
            for si in sindexes]
    for area in areas:
        pts = []
        for s in sections:
            pts += s.find_area(area, 'skull')
        #points.save_pts(pts, area, odir=ptsdir)


def show_sections(sindexes, areas, epsdir='eps/', tmpdir='tmp/'):
    for si in sindexes:
        pylab.figure()
        s = section.load(si, areas=areas, indir=epsdir, tmpdir=tmpdir)
        s.show()
        pylab.show()


if __name__ == '__main__':
    areas = ['V2L', 'AuD', 'Au1', 'AuV', 'PRh', 'V1B', 'V1M', 'TeA', 'Ect']
    si = 71
    if len(sys.argv) > 1:
        si = int(sys.argv[1])
    show_sections([si], areas=areas)
