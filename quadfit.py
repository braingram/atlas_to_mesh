#!/usr/bin/env python

import copy

import numpy
import pylab

import mahotas


def sdist(pts, x, y):
    return numpy.sum((pts - [x, y]) ** 2., 1)


def dist(pts, x, y):
    return numpy.sqrt(sdist(pts, x, y))


def find_closest(pts, mx, my):
    i = sdist(pts, mx, my).argmin()
    return i, pts[i, 0], pts[i, 1]


def find_box_indexes(pts):
    xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
    ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
    # with image coordinates (+y = down)
    i0, _, _ = find_closest(pts, xmin, ymin)
    i1, _, _ = find_closest(pts, xmax, ymin)
    i2, _, _ = find_closest(pts, xmax, ymax)
    i3, _, _ = find_closest(pts, xmin, ymax)
    return i0, i1, i2, i3


def find_box(pts):
    return pts[find_box_indexes]


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


def point_in_triangle(t, pt):
    a, b, c = [numpy.array(p) for p in t]
    p = numpy.array(pt)
    v0 = c - a
    v1 = b - a
    v2 = p - a

    dot00 = numpy.dot(v0, v0)
    dot01 = numpy.dot(v0, v1)
    dot02 = numpy.dot(v0, v2)
    dot11 = numpy.dot(v1, v1)
    dot12 = numpy.dot(v1, v2)

    idenom = 1. / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * idenom
    v = (dot00 * dot12 - dot01 * dot02) * idenom
    return (u >= 0) and (v >= 0) and (u + v < 1)
    if (u >= 0) and (v >= 0) and (u + v < 1):
        pylab.scatter(pt[0], pt[1], c='r')
        return True
    else:
        return False
    #return (u >= 0) and (v >= 0) and (u + v < 1)


def points_in_triangle(t, pts):
    return sum([point_in_triangle(t, p) for p in pts])


def points_in_quad(q, pts):
    p0, p1, p2, p3 = q
    t0 = p0, p1, p2
    t1 = p2, p3, p0
    return points_in_triangle(t0, pts) + points_in_triangle(t1, pts)


def test_quad(p0, p1, p2, p3):
    if any([intersect(p0, p1, p2, p3)[0], \
            intersect(p1, p2, p3, p0)[0]]):
        return False
    return True


def valid_quad(p0, p1, p2, p3, order=0):
    if not test_quad(p0, p1, p2, p3):
        if order == 0:
            return valid_quad(p0, p1, p3, p2, 1)
        elif order == 1:
            return valid_quad(p0, p2, p1, p3, 2)
        raise ValueError("WTF: %s" % ([p0, p1, p2, p3]))
    return p0, p1, p2, p3


def find_perimeter(bim):
    pim = mahotas.bwperim(bim)
    pts = numpy.array(numpy.where(pim))
    if len(pts):
        return pts.T[:, ::-1]
    else:
        return []


def sort_points(pts, start=None):
    selected = numpy.zeros(pts.shape, dtype=bool)
    mpts = numpy.ma.masked_array(pts, selected)
    inds = []
    if start is None:
        x, y = pts.min(0)
    else:
        x, y = start
    while mpts.count():
        i, x, y = find_closest(mpts, x, y)
        mpts.mask[i] = [True, True]
        inds.append(i)
    return pts[inds]


def test_sort_points(pts):
    spts = sort_points(pts)
    pylab.scatter(*spts.T)
    pylab.plot(*spts.T)
    for (i, p) in enumerate(spts):
        pylab.text(p[0], p[1], '%i' % i)


def find_points(bim):
    pts = numpy.array(numpy.where(bim))
    if len(pts):
        return pts.T[:, ::-1]
    else:
        return []


def guess_quad(pts):
    return list(find_box_indexes(pts))


def safe_index(i, n):
    while i >= n:
        i -= n
    while i < 0:
        i += n
    return i


def index_range(si, n, mini, maxi, nitems):
    if mini > si:
        mini -= nitems
    if maxi < si:
        maxi += nitems
    s = max(si - n, mini + 1)
    e = min(si + n, maxi - 1)
    i = s
    #print "IR:", s, e, i, mini, maxi, nitems
    while i <= e:
        yield safe_index(i, nitems)
        i += 1


def maximize_quad_point(qi, ipts, ppts, i, nsearch):
    #oqp = ppts[qi]
    best_i = i
    best_fit = points_in_quad(ppts[qi], ipts)
    print "First:", best_fit
    mini = qi[safe_index(i - 1, len(qi))]
    maxi = qi[safe_index(i + 1, len(qi))]
    if maxi < mini:
        maxi += len(ppts)
    nq = copy.deepcopy(qi)
    #print qi[i], nsearch, mini, maxi, len(ppts)
    for ti in index_range(qi[i], nsearch, mini, maxi, len(ppts)):
        # test if quad is valid, if not, skip
        nq[i] = safe_index(ti, len(ppts))
        #print "Test Quad:", nq
        if test_quad(*ppts[nq]):
            fit = points_in_quad(ppts[nq], ipts)
            #print "\tQ  :", nq
            #print "\tFit:", fit
            if fit > best_fit:
                best_i = ti
                best_fit = fit
        #else:
        #    print "\tBad Quad:", ppts[nq]
    # make best quad
    print "Best :", best_fit
    if best_i == i:
        return qi, best_fit
    else:
        nq[i] = best_i
        return nq, best_fit


def maximize_quad_points(qi, ipts, ppts, nsearch=3, maxi=100, minchange=100):
    maxfit = points_in_quad(ppts[qi], ipts)
    for i in xrange(4):
        qi, fit = maximize_quad_point(qi, ipts, ppts, i, nsearch)
    pinned = [False, False, False, False]
    iteration = 0
    while (not all(pinned)) and (iteration < maxi):
        i = pinned.index(False)
        v = qi[i]
        qi, fit = maximize_quad_point(qi, ipts, ppts, i, nsearch)
        if abs(fit - maxfit) < minchange:
            maxfit = fit
            break
        maxfit = fit
        if (v != qi[i]):  # point was moved
            pinned = [False, False, False, False]
        #pinned[i] = (v == qi[i])
        #print v, qi, pinned
        iteration += 1
    return qi, maxfit


def maximize_quad_edges(qi, ipts, ppts, nsearch=3, maxi=100, minchange=100):
    maxfit = points_in_quad(ppts[qi], ipts)
    for i in xrange(4):
        qi, fit = maximize_quad_edge(i - 1, i, ipts, ppts, i, nsearch)


def fit_quad(bim, **kwargs):
    ipts = find_points(bim)
    ppts = sort_points(find_perimeter(bim))
    qi = guess_quad(ppts)
    qi, fit = maximize_quad_fit(qi, ipts, ppts, **kwargs)
    return ppts[qi], ppts, fit


def test_fit_quad(bim, **kwargs):
    q, pts, fit = fit_quad(bim, **kwargs)
    q = list(q)
    pylab.imshow(bim)
    pylab.title("Fit %i" % fit)
    pylab.scatter(*pts.T, c='b')
    qp = numpy.array(q + q[:1])
    pylab.plot(*qp.T, c='r')
