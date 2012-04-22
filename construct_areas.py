#!/usr/bin/env python

import section
import points


def construct_areas(sindexes, areas, epsdir='eps/', tmpdir='tmp/', \
        ptsdir='pts/'):
    sections = [section.load(si, areas=areas, indir=epsdir, tmpdir=tmpdir) \
            for si in sindexes]
    for area in areas:
        pts = section.find_area(sections, area)
        points.save_pts(pts, area, odir=ptsdir)
