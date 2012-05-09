#!/usr/bin/env python

import cPickle as pickle
import sys

import pylab

import section


default_indices = [i for i in range(12, 162) \
        if not (i in [22, 47, 76, 144, 148])]


def get_points(areas, sections=None):
    """
    Parameters
    ----------
    areas : string or list
        Brain areas to find

    sections : list (optional)
        Sections in which to find areas


    Returns
    -------
    pts : dict or list
        list of points if areas was a string
        dict with keys = areas and values = lists of points
    """
    if isinstance(areas, str):
        areas = [areas]
    if sections is None:
        sections = [section.load(si, areas=areas) for si in default_indices]
    pts = {}
    for area in areas:
        pts[area] = []
        for s in sections:
            pts[area] += [[p.x, p.y, s.get_ap()] for p \
                    in s.find_area(area, 'skull')]
    if len(areas) == 1:
        return pts[areas[0]]
    return pts


def construct_areas(sindexes, areas, epsdir=None, tmpdir=None, \
        ptsdir='pts/'):
    sections = [section.load(si, areas=areas, epsdir=epsdir, tmpdir=tmpdir) \
            for si in sindexes]
    pts = {}
    for area in areas:
        pts[area] = []
        for s in sections:
            pts[area] += [[p.x, p.y, s.get_ap()] for p in \
                    s.find_area(area, 'skull')]
    return pts


def show_sections(sindexes, areas, epsdir=None, tmpdir=None):
    for si in sindexes:
        pylab.figure()
        s = section.load(si, areas=areas, epsdir=epsdir, tmpdir=tmpdir)
        s.show()
        pylab.show()


if __name__ == '__main__':
    areas = ['V2L', 'AuD', 'Au1', 'AuV', 'PRh', 'V1B', 'V1M', 'TeA', 'Ect']
    #areas = ['TeA']
    # skip 22, 47, 76, 144, 148
    sis = [i for i in range(12, 162) if not (i in [22, 47, 76, 144, 148])]
    if len(sys.argv) > 1:
        sis = [int(sys.argv[1])]
    if len(sys.argv) > 2:
        areas = [sys.argv[2]]
    #show_sections(sis, areas=areas, epsdir='/home/graham/Desktop/eps/')
    pts = construct_areas(sis, areas=areas, epsdir=None)
    with open('areas.p', 'w') as ofile:
        pickle.dump(pts, ofile)
