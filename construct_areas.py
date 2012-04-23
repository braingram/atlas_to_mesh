#!/usr/bin/env python

import pickle
import sys

import pylab

import section
#import points


def construct_areas(sindexes, areas, epsdir='eps/', tmpdir='tmp/', \
        ptsdir='pts/'):
    sections = [section.load(si, areas=areas, epsdir=epsdir, tmpdir=tmpdir) \
            for si in sindexes]
    pts = {}
    for area in areas:
        pts[area] = []
        for s in sections:
            pts[area] += s.find_area(area, 'skull')

    with open('areas.p', 'w') as ofile:
        pickle.dump(pts, ofile)


def show_sections(sindexes, areas, epsdir='eps/', tmpdir='tmp/'):
    for si in sindexes:
        pylab.figure()
        s = section.load(si, areas=areas, epsdir=epsdir, tmpdir=tmpdir)
        s.show()
        pylab.show()


if __name__ == '__main__':
    areas = ['V2L', 'AuD', 'Au1', 'AuV', 'PRh', 'V1B', 'V1M', 'TeA', 'Ect']
    # skip 22, 47, 76, 144, 148
    sis = [i for i in range(12, 162) if not (i in [22, 47, 76, 144, 148])]
    if len(sys.argv) > 1:
        sis = [int(sys.argv[1])]
    #show_sections(sis, areas=areas, epsdir='/home/graham/Desktop/eps/')
    construct_areas(sis, areas=areas, epsdir='/home/graham/Desktop/eps/')
