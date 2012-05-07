#!/usr/bin/env python

import sys

import area
import cortex
import points
import section


__all__ = ['area', 'cortex', 'points', 'section']


def run(operation, args):
    oname = 'atlas.operations.%s' % operation
    assert oname in sys.modules, "Unknown operation: %s" % oname
    module = sys.modules[oname]
    assert hasattr(module, 'run'), "Module does not contain run: %s" % module
    return module.run(args)
