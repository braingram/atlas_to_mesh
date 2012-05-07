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
        #print "-- Matrix --"
        #print f.get_matrix(f0, f1)


def tt(x0, y0, x1, y1, f0, f1):
    t(x0, y0, x1, y1, f0, f1)
    t(x1, y1, x0, y0, f1, f0)


def att(f0, f1):
    r0 = [i[1] for i in stack if i[0] == f0][0]
    r1 = [i[1] for i in stack if i[0] == f1][0]
    tt(r0.x0, r0.y0, r1.x0, r1.y0, f0, f1)
    tt(r0.x1, r0.y1, r1.x1, r1.y1, f0, f1)


def draw_rect(r, **kwargs):
    pylab.gca().add_patch(Rectangle((r.x0, r.y0), \
            (r.x1 - r.x0), (r.y1 - r.y0), **kwargs))
    pylab.gca().autoscale_view()
    pylab.gca().set_aspect('equal')
    xs = [r.x0, r.x1, r.x1, r.x0]
    ys = [r.y0, r.y0, r.y1, r.y1]
    c = kwargs.get('ec', 'k')
    for (i, (x, y)) in enumerate(zip(xs, ys)):
        pylab.text(x, y, '%i' % i, color=c)

    pylab.plot(xs[::2], ys[::2], color=c)


def convert_rect(r, f0, f1):
    ul = f.convert(r.x0, r.y0, f0, f1)
    lr = f.convert(r.x1, r.y1, f0, f1)
    return Rect(ul[0], ul[1], lr[0], lr[1])


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

#stack = [('unit', Rect(0, 0, 1, 1)),
#        ('cart', Rect(-1, -1, 2, 2)),
#        ('eps', Rect(86, 87, 908, 625)),
#        ('png', Rect(0, 0, 1600, 1100)),
#        ('skull', Rect(-8, -1, 16, -11))]
stack = [  # (ul.x, ul,y, lr.x, lr.y)
        ('eps', Rect(86, 87, 994, 921)),
        ('png', Rect(0, 0, 1600, 1100)),
        ('skull', Rect(-8, 1, 8, 11))]

names = lambda stack: [i[0] for i in stack]
frames = lambda stack: [i[1] for i in stack]

f = FS(names(stack), frames(stack))

pylab.figure()
ns = len(stack) - 1
for (si, s) in enumerate(stack[:-1]):
    sf = lambda i: pylab.subplot(ns * 100 + 21 + i + (si * 2))
    att(s[0], stack[si + 1][0])
    plot(s[0], stack[si + 1][0], sf)

pylab.figure()
att(stack[0][0], stack[-1][0])
plot(stack[0][0], stack[-1][0])

pylab.show()
