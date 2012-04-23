#!/usr/bin/env python

import collections

import numpy


Point = collections.namedtuple('Point', 'x y frame')
Rect = collections.namedtuple('Rect', 'x y w h')


def tmatrix(f1, f2):
    """
    http://www.senocular.com/flash/tutorials/transformmatrix/
    """
    sx = f2.w / float(f1.w)
    sy = f2.h / float(f1.h)
    tx = float(f2.x - f1.x)
    ty = float(f2.y - f1.y)
    #S = numpy.matrix(numpy.diag([sx, sy, 1.]))
    #T = numpy.matrix(numpy.identity(3))
    #T[:, 2] = [[float(f2.x - f1.x) * sx], [float(f2.y - f1.y) * sy], [1.]]
    #return S * T
    #return T * S
    return numpy.matrix([\
            [sx, 0., tx * sx],
            [0., sx, ty * sy],
            [0., 0., 1.]])
    return numpy.matrix([\
            [f2.w / float(f1.w), 0., float(f2.x - f1.x)],
            [0., f2.h / float(f1.h), float(f2.y - f1.y)],
            [0., 0., 1.]])
    return numpy.matrix([\
            [f2.w / float(f1.w), 0., 0.],
            [0., f2.h / float(f1.h), 0.],
            [float(f2.x - f1.x), float(f2.y - f1.y), 1.]])


class FrameStack(object):
    def __init__(self, names, frames):
        """ frames = dict """
        self.names = names
        self.frames = frames
        self.make_stack()

    def make_stack(self):
        self.stack = {}
        for n1 in self.names:
            self.stack[n1] = {}
            for n2 in self.names:
                self.stack[n1][n2] = self.get_matrix(n1, n2)

    def convert(self, x, y, n1, n2):
        assert(n1  in self.names)
        assert(n2 in self.names)
        if n1 == n2:
            return x, y
        #pt = numpy.array([x, y, 1]) * self.stack[n1][n2]
        pt = self.stack[n1][n2] * numpy.array([[x], [y], [1]])
        #pt = self.stack[n1][n2] * numpy.array([[x, y, 1]])
        #return pt[0, 0] / float(pt[0, 2]), pt[0, 1] / float(pt[0, 2])
        if pt[2, 0] != 1:
            print "inhomogeneous:", pt[2, 0]
        return pt[0, 0], pt[1, 0]

    def get_matrix(self, n1, n2):
        assert(n1  in self.names)
        assert(n2 in self.names)
        if n1 == n2:
            return numpy.matrix(numpy.identity(3))
        i1 = self.names.index(n1)
        i2 = self.names.index(n2)
        if i2 > i1:
            return tmatrix(self.frames[i1], self.frames[i1 + 1]) * \
                    self.get_matrix(self.names[i1 + 1], self.names[i2])
        #if i2 < i1:
        if i1 > i2:
            return numpy.linalg.inv( \
                    tmatrix(self.frames[i2], self.frames[i2 + 1])) * \
                    self.get_matrix(self.names[i1], self.names[i2 + 1])
            #return numpy.linalg.inv( \
            #        tmatrix(self.frames[i2], self.frames[i2 - 1])) * \
            #        self.get_matrix(self.names[i2 - 1], self.names[i1])
            #return tmatrix(self.frames[i1], self.frames[i1 - 1]) * \
            #        self.get_matrix(self.names[i1 - 1], self.names[i2])


def test_framestack():
    nfs = [('unit', Rect(0, 0, 1, 1)),
        ('2x', Rect(0, 0, 2, 2)),
        ('yflip', Rect(0, 0, 2, -2)),
        ('xflip', Rect(0, 0, -2, -2)),
        ('xtran', Rect(1, 0, -2, -2)),
        ('ytran', Rect(1, 1, -2, -2)),
        ('eps', Rect(86, 87, 908, 625)),
        ('png', Rect(0, 0, 1600, 1100)),
        ('skull', Rect(-8, -1, 16, -11))]
    f = FrameStack([i[0] for i in nfs], [i[1] for i in nfs])

    def t(ix, iy, ex, ey, f0, f1):
        cx, cy = f.convert(ix, iy, f0, f1)
        if (abs(float(cx) - float(ex)) > 1E-9) or \
                (abs(float(cy) - float(ey)) > 1E-9):
            print "Error converting (%s, %s) from %s to %s:" % \
                    (ix, iy, f0, f1)
            print "  Expected: %s, %s" % (ex, ey)
            print "  Got     : %s, %s" % (cx, cy)
            print "-- Matrix --"
            print f.get_matrix(f0, f1)
            print

    def tt(x0, y0, x1, y1, f0, f1):
        t(x0, y0, x1, y1, f0, f1)
        t(x1, y1, x0, y0, f1, f0)

    tt(0, 0, 0, 0, 'unit', '2x')
    tt(1, 1, 2, 2, 'unit', '2x')
    tt(0, 0, 0, 0, 'unit', 'yflip')
    tt(1, 1, 2, -2, 'unit', 'yflip')
    tt(0, 0, 0, 0, 'unit', 'xflip')
    tt(1, 1, -2, -2, 'unit', 'xflip')
    #tt(0, 0, -1, 0, 'unit', 'xtran')
    #tt(1, 1, -3, -2, 'unit', 'xtran')
    #tt(1, 1, -3, -2, 'unit', 'ytran')

    tt(86, 87, 0, 0, 'eps', 'png')
    tt(86 + 908, 87 + 625, 1600, 1100, 'eps', 'png')
    tt(0, 0, -8, -1, 'png', 'skull')
    tt(1600, 1100, 8, -12, 'png', 'skull')

    return f


if __name__ == '__main__':
    test_framestack()
