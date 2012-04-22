#!/usr/bin/env python

import collections

import numpy


Point = collections.namedtuple('Point', 'x y frame')
Rect = collections.namedtuple('Rect', 'x y w h')


def tmatrix(f1, f2):
    """
    was:
        im <-> skull <-> lim
    now:
        eps <-> png = labels <-> skull

    eps:
        might be : 86 296 994 921
        bounding box: 0 0 1080 1008

    skull:
        grid : -8, dv, 16, -11

    png & labels:
        upper left = 0 0, right = +, down = +
        dim: 0 0 1600 1100
        dim: 0 0 gw*s gh*s

    : transform :
    from F1 -> F2
        pt_f1([x,y,1]) * M

    where M
        [sx, 0, 0] : sx = F2_w/F1_w
        [0, sy, 0] : sy = F2_h/F1_h
        [tx,ty, 1] : tx = F2_x - F1_x AND ty = F2_y - F1_y
    """
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
        pt = numpy.array([x, y, 1]) * self.stack[n1][n2]
        return pt[0, 0], pt[0, 1]

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
            #return numpy.linalg.inv( \
            #        tmatrix(self.frames[i2], self.frames[i2 - 1])) * \
            #        self.get_matrix(self.names[i2 - 1], self.names[i1])
            return tmatrix(self.frames[i1], self.frames[i1 - 1]) * \
                    self.get_matrix(self.names[i1 - 1], self.names[i2])


def test_framestack():
    nfs = [('unit', Rect(0, 0, 1, 1)),
        ('2x', Rect(0, 0, 2, 2)),
        ('yflip', Rect(0, 0, 2, -2)),
        ('xflip', Rect(0, 0, -2, -2)),
        ('xtran', Rect(1, 0, -2, -2)),
        ('ytran', Rect(1, 1, -2, -2))]
    f = FrameStack([i[0] for i in nfs], [i[1] for i in nfs])

    #TODO more tests here

    # one step
    assert(f.convert(0, 0, 'unit', '2x') == (0., 0.))
    assert(f.convert(1, 1, 'unit', '2x') == (2., 2.))
    # and back
    assert(f.convert(0, 0, '2x', 'unit') == (0., 0.))
    assert(f.convert(2, 2, '2x', 'unit') == (1., 1.))

    # two steps
    # and back
    return f
