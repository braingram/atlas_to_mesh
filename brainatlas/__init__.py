#!/usr/bin/env python

import section
from section import get_closest_section
import construct
import cylinder
import framestack


def area(ml, ap, dv, closest=True, throw=False):
    cs = section.get_closest_section(ap)
    areas = cs.get_area_for_location(ml, dv, 'skull')
    if len(areas) == 1:
        return str(areas[0])
    elif (len(areas) == 0) and closest:
        return section.get_closest_area(ml, dv, ap)
    if not throw:
        return ''
    raise LookupError(
        "Failed to find area at ml: %s, ap: %s, dv: %s" % (ml, ap, dv))


__all__ = ['construct', 'cylinder', 'framestack', 'section',
           'get_closest_section', 'area']
