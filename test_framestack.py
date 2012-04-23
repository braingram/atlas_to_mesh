#!/usr/bin/env python

from matplotlib.patches import Rectangle
import pylab

from framestack import FrameStack as FS
from framestack import Rect, Point


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


def tt(x0, y0, x1, y1, f0, f1):
    t(x0, y0, x1, y1, f0, f1)
    t(x1, y1, x0, y0, f1, f0)


def att(f0, f1):
    r0 = [i[1] for i in stack if i[0] == f0][0]
    r1 = [i[1] for i in stack if i[0] == f1][0]
    tt(r0.x, r0.y, r1.x, r1.y, f0, f1)
    tt(r0.x + r0.w, r0.y + r0.h, r1.x + r1.w, r1.y + r1.h, f0, f1)


def draw_rect(r, **kwargs):
    pylab.gca().add_patch(Rectangle((r.x, r.y), r.w, r.h, **kwargs))
    pylab.gca().autoscale_view()
    pylab.gca().set_aspect('equal')


def convert_rect(r, f0, f1):
    ul = f.convert(r.x, r.y, f0, f1)
    lr = f.convert(r.x + r.w, r.y + r.h, f0, f1)
    return Rect(ul[0], ul[1], lr[0] - ul[0], lr[1] - ul[1])


def plot(f0, f1, sf=lambda i: pylab.subplot(121 + i)):
    r0 = [i[1] for i in stack if i[0] == f0][0]
    r1 = [i[1] for i in stack if i[0] == f1][0]
    sf(0)
    pylab.title(f0)
    draw_rect(r0, ec='b', fc='b', alpha=0.5)
    draw_rect(convert_rect(r1, f1, f0), ec='r', fc='r', alpha=0.5)

    sf(1)
    pylab.title(f1)
    draw_rect(r1, ec='r', fc='r', alpha=0.5)
    draw_rect(convert_rect(r0, f0, f1), ec='b', fc='b', alpha=0.5)

stack = [('unit', Rect(0, 0, 1, 1)),
        ('cart', Rect(-1, -1, 2, 2)),
        ('eps', Rect(86, 87, 908, 625)),
        ('png', Rect(0, 0, 1600, 1100)),
        ('skull', Rect(-8, -1, 16, -11))]

names = lambda stack: [i[0] for i in stack]
frames = lambda stack: [i[1] for i in stack]

f = FS(names(stack), frames(stack))

att('unit', 'cart')
att('cart', 'eps')
att('eps', 'png')
att('png', 'skull')

pylab.figure()
sf = lambda i: pylab.subplot(421 + i)
plot('unit', 'cart', sf)
sf = lambda i: pylab.subplot(423 + i)
plot('cart', 'eps', sf)
sf = lambda i: pylab.subplot(425 + i)
plot('eps', 'png', sf)
sf = lambda i: pylab.subplot(427 + i)
plot('png', 'skull', sf)

pylab.show()
