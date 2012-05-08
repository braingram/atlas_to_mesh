#!/usr/bin/env python

import numpy
import pylab
import scikits.learn.decomposition
import scipy.ndimage

import mahotas


import quadfit


def to_binary(labeled, seed):
    return (labeled == labeled[int(seed.y), int(seed.x)])


def find_points(labeled, seed):
    bim = to_binary(labeled, seed)
    #pim = mahotas.bwperim(bim)
    pts = numpy.array(numpy.where(bim)).astype(numpy.float64)
    if len(pts):
        return pts.T[:, ::-1]
    else:
        return []


def find_corners(labeled, seed):
    pca, pts = pca_transform(labeled, seed, points=True)
    impts = []
    for pt in quadfit.find_box(pts):
        print pt
        impts.append(pca.inverse_transform(pt))
        print impts[-1]
    return tuple(impts)


def pca_transform(labeled, seed, points=False):
    pca = scikits.learn.decomposition.PCA()
    pts = find_points(labeled, seed)
    pca.fit(pts)
    if points:
        return pca, pca.transform(pts)
    return pca


def find_area(labeled, seeds):
    return find_perimeter(labeled, seeds)


def find_perimeter(labeled, seeds):
    """
    return [[x,y],[x,y]...]
    """
    rpts = None
    for seed in seeds:
        bim = to_binary(labeled, seed)
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
