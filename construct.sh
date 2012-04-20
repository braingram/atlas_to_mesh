#!/bin/bash

if [ $1 ]
then
    AREAS=$1
else
    AREAS="V2L AuD Au1 AuV PRh V1B V1M TeA"
fi

echo "Processing $AREAS"

for AREA in $AREAS
do
    for SI in `seq 71 106`
    do
        python find_area.py -i $SI -a $AREA
    done
    sync
    cat points/$AREA\_* > points/$AREA.asc
done
