#!/usr/bin/env python

import optparse
import os
import re
#import sys
import logging

import numpy as np
import pylab as pl
import scipy.ndimage

import mahotas
#from convexhull import convex_hull

# AP coordinates with P = -
bounds = {70: -4.36,
    71: -4.56,
    72: -4.68,
    73: -4.80,
    74: -4.92,
    75: -5.04,
    76: -5.20,
    77: -5.28,
    78: -5.40,
    79: -5.52,
    80: -5.64,
    81: -5.76,
    82: -5.88,
    83: -6.00,
    84: -6.12,
    85: -6.24,
    86: -6.36,
    87: -6.48,
    88: -6.60,
    89: -6.72,
    90: -6.84,
    91: -6.96,
    92: -7.08,
    93: -7.20,
    94: -7.32,
    95: -7.44,
    96: -7.56,
    97: -7.68,
    98: -7.80,
    99: -7.92,
    100: -8.04,
    101: -8.16,
    102: -8.28,
    103: -8.40,
    104: -8.52,
    105: -8.64,
    106: -8.76,
    107: -8.88}

logging.basicConfig(level=logging.DEBUG)

parser = optparse.OptionParser()
parser.add_option("-i", "--sectionIndex", default=71, type='int')
parser.add_option("-a", "--area", default="TeA")
# handle this better
parser.add_option("-t", "--tmpfile", default="tmp/tmp.eps")

(options, args) = parser.parse_args()

dvshift = 0
if options.sectionIndex >= 103:
    dvshift = -1
#    raise NotImplemented("I haven't worked out the -1 mm DV shift yet")

#inFilename = 'eps/071.eps'
inFilename = 'eps/%03i.eps' % options.sectionIndex
tmpFilename = options.tmpfile  # 'tmp.eps'
tmpDir = os.path.dirname(tmpFilename)
area = options.area  # 'TeA'
gridx = (-8, 8)  # left, right: ML
#gridy = (0, -11)  # top, bottom: DV
gridy = (dvshift, dvshift - 11)
gridh = gridy[0] - gridy[1]
gridw = gridx[1] - gridx[0]


# bounding box is lower left and upper right
# 1 -1 scale 0 -1008 translate:
# this flips y (so + is down) then puts origin at 0, -1008 so upper left?
def im_to_skull(x, y, gridx, gridy, bb):
    bbw = bb[2] - bb[0]
    bbh = bb[3] - bb[1]
    hs = gridw / float(bbw)
    vs = gridh / float(bbh)
    cy = y - (1008 - bb[3])
    sx = (x - bb[0]) * hs + gridx[0]
    sy = gridy[0] - cy * vs
    return sx, sy


def skull_to_lim(sx, sy):
    ix = sx * 100 + int(gridw * 100) / 2.
    iy = (sy - dvshift) * -100
    return ix, iy

tf = open(tmpFilename, 'w')
logging.debug("Processing %i for %s" % (options.sectionIndex, area))
with open(inFilename, 'rU') as inFile:
    # find location of labels
    prevLine = ""
    locs = []
    bb = []
    for l in inFile:
        if ' dsh' in l:
            # get rid of the dashed lines for easier segmenting
            logging.debug("Removing dash: %s" % l.strip())
            tf.write('[] 0 dsh\r')
        elif r'%%HiResBoundingBox:' in l:
            # this screws up things like imagemagick
            logging.debug("Skipping high resolution bbox: %s" % l.strip())
        elif re.match(r"^\d\.*\d*\s+\d\.*\d*\s+\d\.*\d*\s+\d\.*\d*\s+cmyk", l):
            # this is a color change line
            if "1 0 0 0" in l:
                #tf.write(l)
                tf.write("1 1 1 1 cmyk\r")
            else:
                tf.write("0 0 0 0 cmyk\r")
        else:
            # pass through other lines
            tf.write(l)
        if ((area != "All") and (area in l)):
            logging.debug("Found %s in: %s" % (area, l.strip()))
            logging.debug("Parsing: %s" % prevLine.strip())
            tokens = prevLine.split()
            if (len(tokens) == 3) and (tokens[2].strip().lower() == 'mov'):
                try:
                    x = float(tokens[0])
                    y = float(tokens[1])
                    locs.append((x, y))
                except Exception as E:
                    logging.error("Error converting tokens to floats")
                    logging.error(str(E))
                    logging.error("Tokens: %s" % str(tokens))
        if r"%%BoundingBox:" in l:
            logging.debug("Found BoundingBox line: %s" % l)
            tokens = l.split()
            try:
                blx = float(tokens[1])
                bly = float(tokens[2])
                bux = float(tokens[3])
                buy = float(tokens[4])
                bb = [blx, bly, bux, buy]
            except Exception as E:
                logging.error("Error converting tokens to floats")
                logging.error(str(E))
                logging.error("Tokens: %s" % str(tokens))
        prevLine = l
logging.debug("Closing temporary file")
tf.close()
logging.debug("Converting temporary file to png")
imFilename = "%s.png" % os.path.splitext(tmpFilename)[0]
cmd = "convert %s -geometry %ix%i %s" %\
        (tmpFilename, int(gridw * 100), int(gridh * 100), imFilename)
logging.debug("\tCommand:%s" % cmd)
p = os.popen(cmd)
logging.debug("Conversion output: %s" % p.read())

logging.debug("Found bounding box: %s" % str(bb))
logging.debug("Found %s at locations %s" % (area, str(locs)))
slocs = []
imxys = []
for loc in locs:
    sloc = im_to_skull(loc[0], loc[1], gridx, gridy, bb)
    logging.debug("Image to Skull: %s to %s" % (str(loc), str(sloc)))
    slocs.append(sloc)
    # convert skull to labeled image coordinates
    imxys.append(list(skull_to_lim(sloc[0], sloc[1])))
    #imxys.append([sloc[0] * 100 + int(gridw * 100) / 2., sloc[1] * -100.])
    logging.debug("Labeled Image coordinate: %s" % str(imxys[-1]))

logging.debug("Labeling image: %s" % imFilename)
im = pl.imread(imFilename).astype(np.uint8)
lim, nr = scipy.ndimage.label(im)
np.save("%s/labeled.npy" % tmpDir, lim)  # save for later
pl.imsave("%s/labeled.png" % tmpDir, lim, cmap=pl.cm.gray)

areaLocations = []
labels = []
tim = np.zeros_like(lim)
index = 0
for xy in imxys:
    label = lim[int(xy[1]), int(xy[0])]
    labels.append(label)
    bim = (lim == label)
    pl.imsave("%s/%i_bim.png" % (tmpDir, index), bim, cmap=pl.cm.gray)
    index += 1
    pim = mahotas.bwperim(bim)
    tim |= pim
    imlocs = np.array(np.where(pim)).astype(np.float64)
    imlocs[1] = (800 - imlocs[1]) / 100.
    imlocs[0] = imlocs[0] / -100. + dvshift
    areaLocations.append(imlocs)
if len(areaLocations) != 0:
    areaLocations = np.hstack(areaLocations)
elif area == 'All':
    #labels = [lim[0,0], lim[-1,0], lim[0,-1], lim[-1,-1]]
    labels = [lim[0, 0], lim[-1, 0], lim[0, -1], lim[-1, -1]]
    logging.debug("All labels: %s" % str(labels))
    bim = (lim != labels[0]) | (lim != labels[1]) | \
            (lim != labels[2]) | (lim != labels[3])
    pim = mahotas.bwperim(bim)
    tim |= pim
    imlocs = np.array(np.where(pim)).astype(np.float64)
    imlocs[1] = (800 - imlocs[1]) / 100.
    imlocs[0] = imlocs[0] / -100. + dvshift
    areaLocations = imlocs
else:
    raise ValueError("Unable to find any points for area: %s" % area)

pl.imsave('%s/areas.png' % tmpDir, tim, cmap=pl.cm.gray)
#pl.scatter(areaLocations[1],areaLocations[0])
#pl.xlim(gridx)
#pl.ylim(gridy[::-1])
#pl.show()
#if False:
#    logging.debug("Finding hull")
#    hull = convex_hull(areaLocations)
#    skull = np.hstack((hull.T,np.ones((hull.shape[1],1)) \
#        *bounds[options.sectionIndex]))

skull = np.hstack((areaLocations.T, np.ones((areaLocations.shape[1], 1)) \
        * bounds[options.sectionIndex]))

logging.debug("Saving")
np.savetxt("points/%s_%03i.asc" % (options.area, options.sectionIndex), skull)
