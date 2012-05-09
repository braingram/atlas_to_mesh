#!/usr/bin/env python

import os
import cPickle as pickle

import numpy
import pylab


def project(x, y, cx, cy):
    """
    Project a 2d point into circular coordinates

    Parameters
    ----------
    x, y : numbers
        Location of 2d point

    cx, cy : numbers
        Center of circle

    Returns
    -------
    angle : float
        Angular component (0: up, +pi/2: right)

    radius : float
        Radial component
    """
    dx = x - cx
    dy = y - cy
    return numpy.arctan2(dx, dy), numpy.sqrt(dx ** 2 + dy ** 2)


def cull_points(pts):
    exts = {}
    for p in pts:
        if p[1] not in exts:
            exts[p[1]] = [p[0], p[0]]
        else:
            if p[0] > exts[p[1]][1]:
                exts[p[1]][1] = p[0]
            if p[0] < exts[p[1]][0]:
                exts[p[1]][0] = p[0]
    mins = [[k, v[0]] for (k, v) in exts.iteritems()]
    maxs = [[k, v[1]] for (k, v) in exts.iteritems()]
    mins = sorted(mins, key=lambda x: x[0])
    maxs = sorted(maxs, key=lambda x: x[0])[::-1]
    return mins + maxs


def plot_area_points(pts, cx, cy, **kwargs):
    """
    Project points onto the cylinder surface then plot

    Parameters
    ----------
    pts : list of 3D lists
        List of area points (ML, DV, AP)

    kwargs : dict
        Keyword arguments to pass on to pylab.fill

    See Also
    --------
    pylab.fill
    """
    cpts = numpy.array(cull_points( \
            [[project(p[0], p[1], cx, cy)[0], p[2]] for p in pts]))
    pylab.fill(cpts[:, 0], cpts[:, 1], **kwargs)


if __name__ == '__main__':
    ptsfile = 'areas.p'
    meshdir = 'meshes'

    cx, cy = (0., 6.)  # ml, dv

    # ap -> x
    # theta (cylindrical projection in ml/dv) -> y

    def to_cylindrical(x, y):
        # return theta, r
        dx = x - cx
        dy = y - cy
        return numpy.arctan2(dx, dy), numpy.sqrt(dx ** 2 + dy ** 2)

    pts = pickle.load(open(ptsfile, 'r'))

    areas = pts.keys()

    def get_color(area):
        i = areas.index(area)
        i /= float(len(areas))
        return pylab.cm.jet(i)

    def test_p(area, p):
        if p[0] < 0:
            return False
        return True

    def cull(pts):
        exts = {}
        for p in pts:
            if p[1] not in exts:
                exts[p[1]] = [p[0], p[0]]
            else:
                if p[0] > exts[p[1]][1]:
                    exts[p[1]][1] = p[0]
                if p[0] < exts[p[1]][0]:
                    exts[p[1]][0] = p[0]
        mins = [[k, v[0]] for (k, v) in exts.iteritems()]
        maxs = [[k, v[1]] for (k, v) in exts.iteritems()]
        mins = sorted(mins, key=lambda x: x[0])
        maxs = sorted(maxs, key=lambda x: x[0])[::-1]
        return mins + maxs

    rpts = {}
    for area in areas:
        rpts[area] = []

        # project to cylindrical coordinates
        # project to x, y
        rpts[area] = [[to_cylindrical(p[0], p[1])[0], p[2]] for p in \
                pts[area] if test_p(area, p)]

        apts = numpy.array(list(cull(rpts[area])))

        pylab.scatter(apts[:, 0], apts[:, 1], c=get_color(area), label=area)
        pylab.fill(apts[:, 0], apts[:, 1], color=get_color(area))

    # plot flattened cortex
    pylab.xlabel('AP')
    pylab.ylabel('Cortical Surface')
    pylab.legend()
    pylab.show()
