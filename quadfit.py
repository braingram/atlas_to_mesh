#!/usr/bin/env python

import numpy
import pylab

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


def find_box(pts):
    xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
    ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
    # with image coordinates (+y = down)
    _, ulx, uly = find_closest(pts, xmin, ymin)
    _, urx, ury = find_closest(pts, xmax, ymin)
    _, lrx, lry = find_closest(pts, xmax, ymax)
    _, llx, lly = find_closest(pts, xmin, ymax)
    return (ulx, uly), (urx, ury), (lrx, lry), (llx, lly)


def calc_line(p0, p1):
    d = p0[0] - p1[0]
    if d == 0:
        d = 1E-32
    a = (p0[1] - p1[1]) / float(d)
    b = p0[1] - a * p0[0]
    return a, b


def intersect(p0, p1, p2, p3):
    """
    if lines parallel and overlapping, returns false
    """
    if max(p0[0], p1[0]) < min(p2[0], p3[0]):
        return False, None
    a0, b0 = calc_line(p0, p1)
    a1, b1 = calc_line(p2, p3)
    if a0 == a1:
        return False, None
    xa = (b1 - b0) / (a0 - a1)
    print xa
    if xa > min(p0[0], p1[0]) and xa < max(p0[0], p1[0]):
        return True, (xa, a0 * xa + b0)
    return False, None


def plot_intersect(p0, p1, p2, p3):
    b, xy = intersect(p0, p1, p2, p3)

    def plot_line(p0, p1, **kwargs):
        pylab.plot([p0[0], p1[0]], [p0[1], p1[1]], **kwargs)

    plot_line(p0, p1, c='b')
    plot_line(p2, p3, c='g')
    if b:
        pylab.title('intersect')
        pylab.scatter([xy[0]], [xy[1]], c='r')
    else:
        pylab.title('none')


def test_quad(p0, p1, p2, p3):
    if any(intersect(p0, p1, p2, p3), \
            intersect(p1, p2, p3, p0)):
        return False
    return True


def quad(p0, p1, p2, p3, order=0):
    if not test_quad(p0, p1, p2, p3):
        if order == 0:
            return quad(p0, p1, p3, p2, 1)
        elif order == 1:
            return quad(p0, p2, p1, p3, 2)
        raise ValueError("WTF: %s" % ([p0, p1, p2, p3]))
    return p0, p1, p2, p3


def find_perimeter(bim):
    pim = mahotas.bwperim(bim)
    pts = numpy.array(numpy.where(pim))
    if len(pts):
        return pts.T[:, ::-1]
    else:
        return []


def find_points(bim):
    pts = numpy.array(numpy.where(bim))
    if len(pts):
        return pts.T[:, ::-1]
    else:
        return []


def guess_quad(pts):
    return find_box(pts)


def fit_quad(bim):
    ipts = find_points(bim)
    ppts = find_perimeter(bim)
    q = guess_quad(ppts)
