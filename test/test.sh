#!/bin/bash

atlas.py section 6.5 3.5 -7
atlas.py section 6.5 3.5 -7 -ps
atlas.py area 6.5 3.5 -7
atlas.py points -p areas.p
atlas.py points V2L -m -A areas.p
atlas.py cortex 6.5 3.5 -7 -ps -A areas.p
