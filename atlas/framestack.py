#!/usr/bin/env python

import collections


Point = collections.namedtuple('Point', 'x y frame')
Rect = collections.namedtuple('Rect', 'x0 y0 x1 y1')


class Frame(object):
    def __init__(self, rect):
        self.rect = rect
        self.x = rect.x0
        self.y = rect.y0
        self.width = float(rect.x1 - rect.x0)
        self.height = float(rect.y1 - rect.y0)
        assert(self.width != 0)
        assert(self.height != 0)
        assert(self.width > 0)
        assert(self.height > 0)

    def remove_origin(self, x, y):
        return x - self.x, y - self.y

    def add_origin(self, x, y):
        return x + self.x, y + self.y

    def grow(self, x, y):
        return x * self.width, y * self.height

    def shrink(self, x, y):
        return x / self.width, y / self.height

    def to_unit(self, x, y):
        return self.shrink(*self.remove_origin(x, y))

    def from_unit(self, x, y):
        return self.add_origin(*self.grow(x, y))


class FrameStack(object):
    def __init__(self, names, rects):
        """ frames = dict """
        self.names = names
        self.rects = rects
        self.frames = {}
        for (n, r) in zip(names, rects):
            self.frames[n] = Frame(r)

    def convert(self, x, y, n1, n2):
        return self.frames[n2].from_unit(*self.frames[n1].to_unit(x, y))
