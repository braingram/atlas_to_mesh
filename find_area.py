#!/usr/bin/env python

import optparse
import os
import re
#import sys
import logging

import numpy as np
import pylab as pl
import scipy.ndimage

import mahotas

areas = ['V2L', 'AuD', 'Au1', 'AuV', 'PRh', 'V1B', 'V1M', 'TeA', 'Ect']

# bounding box is lower left and upper right
# 1 -1 scale 0 -1008 translate:
# this flips y (so + is down) then puts origin at 0, -1008 so upper left?
def im_to_skull(x, y, gridx, gridy, gridw, gridh, bb):
    bbw = bb[2] - bb[0]
    bbh = bb[3] - bb[1]
    hs = gridw / float(bbw)
    vs = gridh / float(bbh)
    cy = y - (1008 - bb[3])
    sx = (x - bb[0]) * hs + gridx[0]
    sy = gridy[0] - cy * vs
    return sx, sy


def skull_to_lim(sx, sy, gridw, dvshift):
    ix = sx * 100 + int(gridw * 100) / 2.
    iy = (sy - dvshift) * -100
    return ix, iy


def process_section(index, areas):
    locs, bb = make_tmpfile(inFilename, tmpFilename, areas, gridw, gridh)

    # partially apply function
    im_to_s = lambda x, y: im_to_skull(x, y, gridx, gridy, \
            gridw, gridh, bb)
    s_to_lim = lambda sx, sy: skull_to_lim(sx, sy, gridw, dvshift)
    slocs, imxys = convert_locations(locs, im_to_s, s_to_lim)
    lim = make_labeled_image(tmpFilename, tmpDir)
    skull = find_labels(imxys, lim, AP, dvshift)
    save(skull, index)


def make_tmpfile(inFilename, tmpFilename, areas, gridw, gridh):
    return locs, bb


def convert_locations(locs, im_to_s, s_to_lim):
    slocs = {}
    imxys = {}
    for area in locs.keys():
        slocs[area] = []
        imxys[area] = []
        for loc in locs[area]:
            sloc = im_to_s(loc[0], loc[1])
            slocs[area].append(sloc)
            imxys[area].append(list(s_to_lim(sloc[0], sloc[1])))
    return slocs, imxys


def make_labeled_image(filename, tmpDir):
    return lim


def find_labels(imxys, lim, AP, dvshift):
    skull = {}
    for area in imxys.keys():
        areaLocs = []
        for xy in imxys[area]:
            label = lim[int(xy[1]), int(xy[0])]
            bim = (lim == label)
            pim = mahotas.bwperim(bim)
            imlocs = np.array(np.where(pim)).astype(np.float64)
            imlocs[1] = (800 - imlocs[1]) / 100.
            imlocs[0] = imlocs[0] / -100. + dvshift
            areaLocs.append(imlocs)
        if len(areaLocs) != 0:
            areaLocs = np.hstack(areaLocs)
        skull[area] = np.hstack((areaLocs.T, np.ones((areaLocs.shape[1], 1)) \
                * AP))
    return skull


def save(skull, index):
    for area in skull.keys():
        pts = skull[area]
        np.savetxt("points/%s_%03i.asc" % (area, index), pts)
