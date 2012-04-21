#!/bin/bash

AREAS="All V2L AuD Au1 AuV PRh V1B V1M TeA Ect"

for AREA in $AREAS
do
    cp points/$AREA.ply meshes/
done
