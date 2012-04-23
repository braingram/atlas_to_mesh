#!/usr/bin/env python

import numpy
import pylab
import scipy.ndimage

import mahotas


def sdist(x0, y0, x1, y1):
    return (x0 - x1) ** 2. + (y0 - y1) ** 2.


def dist(x0, y0, x1, y1):
    return numpy.sqrt(sdist(x0, y0, x1, y1))


def find_closest(pts, mx, my):
    mi = 0
    mv = sdist(pts[0][0], pts[0][1], mx, my)
    for (i, p) in enumerate(pts):
        d = sdist(p[0], p[1], mx, my)
        if d < mv:
            mi = i
            mv = d
    return mi, pts[mi][0], pts[mi][1]


def guess_start(pts, width, height):
    mx = width / 2.
    my = height / 2.

    # find point closest to center : probably a corner?
    i, x, y = find_closest(pts, mx, my)
    return i, x, y


def vectorize(labeled, seeds):
    pts = find_perimeter(labeled, seeds)

    # fit 2 curves and 2 straight lines
    height, width = labeled.shape[:2]
    start = guess_start(pts, width, height)
    return start


def find_area(labeled, seeds):
    return find_perimeter(labeled, seeds)


def find_perimeter(labeled, seeds):
    """
    return [[x,y],[x,y]...]
    """
    rpts = None
    for seed in seeds:
        label = labeled[int(seed.y), int(seed.x)]
        bim = (labeled == label)
        pim = mahotas.bwperim(bim)
        pts = numpy.array(numpy.where(pim)).astype(numpy.float64)
        if len(pts):
            if rpts is None:
                rpts = pts
            else:
                rpts = numpy.hstack((rpts, pts))
    if rpts is None:
        return []
    else:
        return rpts.T[:, ::-1]  # swap dimensions to get to (x, y)
