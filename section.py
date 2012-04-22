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

# max index = 161 (last coronal section)
# bounding box is good up till there

bounds = {70: -4.36, 71: -4.56, 72: -4.68, 73: -4.80, 74: -4.92, 75: -5.04,
    76: -5.20, 77: -5.28, 78: -5.40, 79: -5.52, 80: -5.64, 81: -5.76,
    82: -5.88, 83: -6.00, 84: -6.12, 85: -6.24, 86: -6.36, 87: -6.48,
    88: -6.60, 89: -6.72, 90: -6.84, 91: -6.96, 92: -7.08, 93: -7.20,
    94: -7.32, 95: -7.44, 96: -7.56, 97: -7.68, 98: -7.80, 99: -7.92,
    100: -8.04, 101: -8.16, 102: -8.28, 103: -8.40, 104: -8.52, 105: -8.64,
    106: -8.76, 107: -8.88}


#Point = collections.namedtuple('Point', 'x y frame')
#Rect = collections.namedtuple('Rect', 'x y w h')


def get_grid_rect(index):
    assert(type(index) == int)
    assert(index > 0)
    assert(index < 162)
    if index > 102:
        return Rect(-8, -1, 16, -11)
    if index > 11:
        return Rect(-8, 0, 16, -11)
    if index > 5:
        return Rect(-7, 0, 14, -10)
    return Rect(-5, -1, 10, -8)
    #gridx = (-8, 8)
    #dv = get_dv_shift(index)
    #gridy = (dv, dv - 11)
    #gridw = gridx[1] - gridx[0]
    #gridh = gridy[0] - gridy[1]
    #return gridx, gridy, gridw, gridh


def get_bounding_rect(index):
    assert(type(index) == int)
    assert(index > 0)
    assert(index < 162)
    if index > 11:
        return Rect(86, 296, 994, 921)
    raise NotImplementedError("No bounding box for sections < 12")


def get_png_rect(index, scale):
    grid = get_grid_rect(index)
    return Rect(0, 0, abs(grid.w * scale), abs(grid.h * scale))


class Section(object):
    def __init__(self, index, areas=None, indir='eps/', tmpdir='tmp/'):
        self.scale = 100  # pixels per eps unit
        self.index = index
        self.ap = None  # bounds[index]: check this later

        if areas is None:
            areas = []
        self.areas = {}
        for area in areas:
            self.areas[area] = []

        self.process_eps_file(indir, tmpdir)
        self.setup_frames()

    def process_eps_file(self, epsdir, tmpdir='tmp/'):
        """
        get tag locations and bounding box
        """
        bb = get_bounding_rect(self.index)
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
                    # possibly overwrite bounding box to 0 0 1080 1008
                    temp_file.write(l)

                # find areas
                for area in self.areas.keys():
                    if area_in_line(area, l):
                        x, y = find_area(prev_line)
                        self.areas[area].append(Point(x, y, 'eps'))

                if r"mm) sh" in l:
                    self.ap = parse_ap(l)
                # find bounding box
                #if r"%%BoundingBox:" in l:
                #    # possibly overwrite bounding box to 0 0 1080 1008
                #    tokens = l.split()
                #    try:
                #        blx = float(tokens[1])
                #        bly = float(tokens[2])
                #        bux = float(tokens[3])
                #        buy = float(tokens[4])
                #        self.eps_bb = [blx, bly, bux, buy]
                #    except Exception as E:
                #        logging.error("Error converting tokens to floats")
                #        logging.error(str(E))
                #        logging.error("Tokens: %s" % str(tokens))
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
                ('eps', 'png', 'skulll'),
                (eps, png, skull))


def parse_ap(line):
    try:
        ap = int(line.split('(')[1].strip().split()[0])
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


def find_area(area, line):
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


def load(index, areas=None, indir='eps/', tmpdir='tmp/'):
    return Section(index, areas=areas, indir=indir, tmpdir=tmpdir)
