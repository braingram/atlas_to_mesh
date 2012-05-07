#!/usr/bin/env python


import os
import cPickle as pickle

import numpy
import pylab


ptsfile = 'areas.p'
meshdir = 'meshes'

pts = pickle.load(open(ptsfile, 'r'))

areas = pts.keys()


if not os.path.exists(meshdir):
    os.makedirs(meshdir)

for area in areas:
    fn = os.path.join(meshdir, area) + '.asc'
    apts = numpy.array(pts[area])
    numpy.savetxt(fn, apts)

# use meshlab to make meshes
