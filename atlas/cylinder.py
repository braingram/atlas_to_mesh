#!/usr/bin/env python

import os
import cPickle as pickle

import numpy
import pylab


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

    ap_extremes = {}

    def test_p(area, p):
        if p[0] < 0:
            return False
        return True
        #if area not in ap_extremes:
        #    ap_extremes[area] = {}
        #    ap_extremes[area][p[2]] = [p[0], p[0]]
        #    return True
        #if p[2] not in ap_extremes[area]:
        #    ap_extremes[area][p[2]] = [p[0], p[0]]
        #    return True
        #emin, emax = ap_extremes[area][p[2]]
        #if p[0] < emin:
        #    ap_extremes[area][p[2]][0] = p[0]
        #    return True
        #if p[0] > emax:
        #    ap_extremes[area][p[2]][1] = p[0]
        #    return True
        #return False

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
