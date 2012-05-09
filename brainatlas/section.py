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
bounds = {12: 2.76, 13: 2.52, 14: 2.28, 15: 2.16, 16: 2.04, 17: 1.92, 18: 1.8,
        19: 1.68, 20: 1.56, 21: 1.44, 23: 1.2, 24: 1.08, 25: 0.96, 26: 0.84,
        27: 0.72, 28: 0.6, 29: 0.48, 30: 0.36, 31: 0.24, 32: 0.12, 33: 0.0,
        34: -0.12, 35: -0.24, 36: -0.36, 37: -0.48, 38: -0.6, 39: -0.72,
        40: -0.84, 41: -0.96, 42: -1.08, 43: -1.2, 44: -1.32, 45: -1.44,
        46: -1.56, 48: -1.8, 49: -1.92, 50: -2.04, 51: -2.16, 52: -2.28,
        53: -2.4, 54: -2.52, 55: -2.64, 56: -2.76, 57: -2.92, 58: -3.0,
        59: -3.12, 60: -3.24, 61: -3.36, 62: -3.48, 63: -3.6, 64: -3.72,
        65: -3.84, 66: -3.96, 67: -4.08, 68: -4.2, 69: -4.36, 70: -4.44,
        71: -4.56, 72: -4.68, 73: -4.8, 74: -4.92, 75: -5.04, 77: -5.28,
        78: -5.4, 79: -5.52, 80: -5.64, 81: -5.76, 82: -5.88, 83: -6.0,
        84: -6.12, 85: -6.24, 86: -6.36, 87: -6.48, 88: -6.6, 89: -6.72,
        90: -6.84, 91: -6.96, 92: -7.08, 93: -7.2, 94: -7.32, 95: -7.44,
        96: -7.56, 97: -7.68, 98: -7.8, 99: -7.92, 100: -8.04, 101: -8.16,
        102: -8.28, 103: -8.4, 104: -8.52, 105: -8.64, 106: -8.76, 107: -8.88,
        108: -9.0, 109: -9.12, 110: -9.24, 111: -9.36, 112: -9.48, 113: -9.6,
        114: -9.72, 115: -9.84, 116: -9.96, 117: -10.08, 118: -10.2,
        119: -10.32, 120: -10.44, 121: -10.56, 122: -10.68, 123: -10.8,
        124: -10.92, 125: -11.04, 126: -11.16, 127: -11.28, 128: -11.4,
        129: -11.52, 130: -11.64, 131: -11.76, 132: -11.88, 133: -12.0,
        134: -12.12, 135: -12.24, 136: -12.36, 137: -12.48, 138: -12.6,
        139: -12.72, 140: -12.84, 141: -12.96, 142: -13.08, 143: -13.2,
        145: -13.44, 146: -13.56, 147: -13.68, 149: -13.92, 150: -14.04,
        151: -14.16, 152: -14.28, 153: -14.4, 154: -14.52, 155: -14.64,
        156: -14.76, 157: -15.0, 158: -15.24, 159: -15.48, 160: -15.72,
        161: -15.96}


default_areas = ['V2L', 'AuD', 'Au1', 'AuV', 'PRh', 'V1B', 'V1M', 'TeA', 'Ect']


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


def get_eps_dir(epsdir=None):
    if epsdir is None:
        return os.path.join(os.path.dirname(__file__), 'eps')


def get_tmp_dir(tmpdir=None):
    if tmpdir is None:
        tmpdir = '/tmp/pyatlas/'
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    return tmpdir


class Section(object):
    def __init__(self, index, areas=None, epsdir=None, tmpdir=None):
        self.scale = 100  # pixels per eps unit
        self.index = index
        self.ap = None  # bounds[index]: check this later

        if areas is None:
            areas = default_areas
        self.areas = {}
        for area in areas:
            self.areas[area] = []

        self.label_to_area = {}
        self.area_to_label = {}
        self.epsdir = get_eps_dir(epsdir)
        self.tmpdir = get_tmp_dir(tmpdir)
        self.process_eps_file(self.epsdir, self.tmpdir)
        self.setup_frames()
        self.make_label_area_mapping()

    def process_eps_file(self, epsdir, tmpdir):
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

    def get_section_image_filename(self):
        bb = get_bounding_box(self.index)
        input_fn = "%s/%03i.eps" % (self.epsdir, self.index)
        temp_fn = "%s/c%03i.eps" % (self.tmpdir, self.index)
        with open(input_fn, 'rU') as input_file, \
                open(temp_fn, 'w') as temp_file:
            for l in input_file:
                # clean up file
                if r'%%HiResBoundingBox:' in l:  # this fubars imagemagick
                    pass
                elif r"%%BoundingBox:" in l:
                    # overwrite bounding box
                    temp_file.write( \
                            r"%%BoundingBox: " + "%i %i %i %i\r" % tuple(bb))
                else:
                    temp_file.write(l)

        _, _, pw, ph = get_png_rect(self.index, self.scale)
        return convert_eps(temp_fn, pw, ph)

    def get_section_image(self):
        return pylab.imread(self.get_section_image_filename())

    def get_ap(self):
        if self.ap is None:
            logging.debug("No ap found when parsing")
            return bounds[self.index]
        if (bounds.get(self.index, self.ap) != self.ap):
            logging.error("Parsed ap[%s] != bounds ap %s" % \
                    (self.ap, bounds[self.index]))
        return self.ap

    def get_area_for_location(self, x, y, frame):
        lx, ly = self.frame_stack.convert(x, y, frame, 'png')
        label = self.labeled[int(ly), int(lx)]
        if label in self.label_to_area:
            return self.label_to_area[label]
        else:
            self.make_label_area_mapping()
            if label not in self.label_to_area:
                raise ValueError("Unknown label %s at %i %i" % \
                        (label, int(lx), int(ly)))
            else:
                return self.label_to_area[label]

    def make_label_area_mapping(self):
        self.label_to_area = {}
        self.area_to_label = {}
        for area in self.areas.keys():
            if area not in self.area_to_label:
                self.area_to_label[area] = []
            for pt in self.areas[area]:
                ppt = self.frame_stack.convert(pt.x, pt.y, pt.frame, 'png')
                label = self.labeled[int(ppt[1]), int(ppt[0])]
                if label not in self.label_to_area:
                    self.label_to_area[label] = []
                self.label_to_area[label].append(area)
                self.area_to_label[area].append(label)

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


def load(index, areas=None, epsdir=None, tmpdir=None):
    return Section(index, areas=areas, epsdir=epsdir, tmpdir=tmpdir)


def get_closest_section(ap, mode=None, **kwargs):
    index = -1  # this gets the index just before the break
    for i in sorted(bounds.keys()):
        ref_ap = bounds[i]
        if ref_ap < ap:
            break
        index = i
    return Section(index, **kwargs)
