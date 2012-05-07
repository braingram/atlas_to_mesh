#!/usr/bin/env python

#import collections
import logging
import os
import re

import numpy
import pylab
import scipy.ndimage

import framestack
from framestack import Rect, Point

import vision

# max index = 161 (last coronal section)
# bounding box is good up till there

# messed up sections
#  w/bad eps parsing:
#   22, 47, 76, 144, 148
#  : 022 (bad eps parsing)

bounds = {70: -4.36, 71: -4.56, 72: -4.68, 73: -4.80, 74: -4.92, 75: -5.04,
    76: -5.20, 77: -5.28, 78: -5.40, 79: -5.52, 80: -5.64, 81: -5.76,
    82: -5.88, 83: -6.00, 84: -6.12, 85: -6.24, 86: -6.36, 87: -6.48,
    88: -6.60, 89: -6.72, 90: -6.84, 91: -6.96, 92: -7.08, 93: -7.20,
    94: -7.32, 95: -7.44, 96: -7.56, 97: -7.68, 98: -7.80, 99: -7.92,
    100: -8.04, 101: -8.16, 102: -8.28, 103: -8.40, 104: -8.52, 105: -8.64,
    106: -8.76, 107: -8.88}


def get_grid_rect(index):
    assert(type(index) == int)
    assert(index > 0)
    assert(index < 162)
    if index > 102:
        return Rect(-8, 1, 8, 12)
    if index > 11:
        return Rect(-8, 0, 8, 11)
    if index > 5:
        return Rect(-7, 0, 7, 10)
    return Rect(-5, 1, 5, 9)
    #gridx = (-8, 8)
    #dv = get_dv_shift(index)
    #gridy = (dv, dv - 11)
    #gridw = gridx[1] - gridx[0]
    #gridh = gridy[0] - gridy[1]
    #return gridx, gridy, gridw, gridh


def get_bounding_rect(index):
    # eps coordinates are 0,0 = lower left
    # atlas files use a translated and scaled version
    #   1 -1 scale 0 -1008 translate
    # however this is AFTER the bounding box
    bb = get_bounding_box(index)
    y0 = 1008 - bb.y1
    y1 = 1008 - bb.y0
    return Rect(bb.x0, y0, bb.x1, y1)


def get_bounding_box(index):
    """
    llx, lly, urx, ury
    """
    assert(type(index) == int)
    assert(index > 0)
    assert(index < 162)
    if index > 11:
        return Rect(86, 296, 994, 921)
    raise NotImplementedError("No bounding box for sections < 12")
    #r = get_bounding_rect(index)
    #return r.x, r.y, r.w - r.x, r.h - r.y


def get_png_rect(index, scale):
    grid = get_grid_rect(index)
    w = (grid.x1 - grid.x0) * scale
    h = (grid.y1 - grid.y0) * scale
    return Rect(0, 0, w, h)


class Section(object):
    def __init__(self, index, areas=None, epsdir='eps/', tmpdir='tmp/'):
        self.scale = 100  # pixels per eps unit
        self.index = index
        self.ap = None  # bounds[index]: check this later

        if areas is None:
            areas = []
        self.areas = {}
        for area in areas:
            self.areas[area] = []

        self.epsdir = epsdir
        self.tmpdir = tmpdir
        self.process_eps_file(epsdir, tmpdir)
        self.setup_frames()

    def process_eps_file(self, epsdir, tmpdir='tmp/'):
        """
        get tag locations and bounding box
        """
        bb = get_bounding_box(self.index)
        input_fn = "%s/%03i.eps" % (epsdir, self.index)
        temp_fn = "%s/%03i.eps" % (tmpdir, self.index)
        #temp_file = open("%s
        with open(input_fn, 'rU') as input_file, \
                open(temp_fn, 'w') as temp_file:
            prev_line = ""
            for l in input_file:
                # clean up file
                if ' dsh' in l:  # remove dashed lines
                    temp_file.write('[] 0 dsh\r')
                elif r'%%HiResBoundingBox:' in l:  # this fubars imagemagick
                    prev_line = l
                    pass
                elif re.match(\
                    r"^\d\.*\d*\s+\d\.*\d*\s+\d\.*\d*\s+\d\.*\d*\s+cmyk", l):
                    if "1 0 0 0" in l:
                        temp_file.write("1 1 1 1 cmyk\r")
                    else:
                        temp_file.write("0 0 0 0 cmyk\r")
                elif r"%%BoundingBox:" in l:
                    # overwrite bounding box
                    temp_file.write( \
                            r"%%BoundingBox: " + "%i %i %i %i\r" % tuple(bb))
                else:
                    temp_file.write(l)

                # find areas
                if l[0] != r"%":
                    for area in self.areas.keys():
                        if area_in_line(area, l):
                            try:
                                x, y = find_label_on_line(area, prev_line)
                                self.areas[area].append(Point(x, y, 'eps'))
                            except Exception as E:
                                logging.error("Section[%s]: Line[%s] contained"
                                " area[%s], prev_line[%s] did not parse to "
                                "location[%s]" % (self.index, l, area, \
                                        prev_line, E))

                if r"mm) sh" in l:
                    self.ap = parse_ap(l)
                prev_line = l
        _, _, pw, ph = get_png_rect(self.index, self.scale)
        self.png_filename = convert_eps(temp_fn, pw, ph)
        self.labeled = label_image(self.png_filename)

    def get_ap(self):
        if self.ap is None:
            logging.debug("No ap found when parsing")
            return bounds[self.index]
        if (bounds.get(self.index, self.ap) != self.ap):
            logging.error("Parsed ap[%s] != bounds ap %s" % \
                    (self.ap, bounds[self.index]))
        return self.ap

    def setup_frames(self):
        eps = get_bounding_rect(self.index)
        png = get_png_rect(self.index, self.scale)
        skull = get_grid_rect(self.index)
        self.frame_stack = framestack.FrameStack(\
                ('eps', 'png', 'skull'),
                (eps, png, skull))

    def search_for_area(self, area):
        self.areas[area] = []
        temp_fn = "%s/%03i.eps" % (self.tmpdir, self.index)
        with open(temp_fn, 'rU') as temp_file:
            prev_line = ""
            for l in temp_file:
                for area in self.areas.keys():
                    if area_in_line(area, l):
                        try:
                            x, y = find_label_on_line(area, prev_line)
                            self.areas[area].append(Point(x, y, 'eps'))
                        except Exception as E:
                            logging.error("Section[%s]: Line[%s] contained "
                            "area[%s], prev_line[%s] did not parse to "
                            "location[%s]" % (self.index, l, area, \
                                    prev_line, E))
                prev_line = l

    def find_label(self, area, frame):
        if area not in self.areas:
            self.search_for_area(area)
        pts = self.areas[area]  # pts (in eps)
        npts = []
        for pt in pts:
            npt = self.frame_stack.convert(pt.x, pt.y, pt.frame, frame)
            npts.append(Point(npt[0], npt[1], frame))
        return npts

    def find_area(self, area, frame):
        labels = self.find_label(area, 'png')
        pts = vision.find_area(self.labeled, labels)
        rpts = []
        for pt in pts:
            npt = self.frame_stack.convert(pt[0], pt[1], 'png', frame)
            rpts.append(Point(npt[0], npt[1], frame))
        return rpts

    def show(self):
        # show labeled image
        pylab.imshow(self.labeled)
        pylab.title("Section %03i AP:%.3f" % (self.index, self.ap))
        for area in self.areas.keys():
            pts = self.find_label(area, 'png')
            spts = self.find_label(area, 'skull')
            xys = numpy.array([[pt.x, pt.y] for pt in pts])
            if len(xys):
                pylab.scatter(xys[:, 0], xys[:, 1], c='k')
                for (pt, spt) in zip(pts, spts):
                    l = "%s:[%.2f, %.2f, %.2f]" % (area, spt.x, spt.y, self.ap)
                    pylab.text(pt.x, pt.y, l)
            #rpts = [Point(86, 87, 'eps'), Point(994, 87, 'eps'),
            #        Point(994, 712, 'eps'), Point(86, 712, 'eps')]
            #for (i, pt) in enumerate(rpts):
            #    x, y = self.frame_stack.convert(pt.x, pt.y, pt.frame, 'png')
            #    pylab.scatter(x, y, c='k')
            #    pylab.text(x, y, 'Test:%i' % i)


def parse_ap(line):
    try:
        ap = float(line.split('(')[1].strip().split()[0])
        logging.debug("Parsed AP[%s] from %s" % (ap, line))
        return ap
    except Exception as E:
        logging.error("Failed[%s] to parse ap from %s" % (E, line))
    return None


def area_in_line(area, line):
    if area == 'All':
        return False
    if area in line:
        return True
    return False


def find_label_on_line(area, line):
    tokens = line.split()
    if (len(tokens) == 3) and (tokens[2].strip().lower() == 'mov'):
        try:
            x = float(tokens[0])
            y = float(tokens[1])
            return x, y
        except Exception as E:
            logging.error("Error[%s] parsing area[%s] line[%s]" % \
                    (E, area, line))
            logging.error("\tTokens: %s" % tokens)
            raise E


def convert_eps(filename, width, height):
    ofilename = "%s.png" % os.path.splitext(filename)[0]
    cmd = "convert %s -geometry %ix%i %s" %\
            (filename, int(width), int(height), ofilename)
    logging.debug("\tCommand:%s" % cmd)
    p = os.popen(cmd)
    logging.debug("Conversion output: %s" % p.read())
    return ofilename


def label_image(filename):
    im = pylab.imread(filename).astype(numpy.uint8)
    lim, _ = scipy.ndimage.label(im)
    return lim


def load(index, areas=None, epsdir='eps/', tmpdir='tmp/'):
    return Section(index, areas=areas, epsdir=epsdir, tmpdir=tmpdir)
