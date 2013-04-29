#!/bin/sh

PPN=16
for var in {1..5}
do
    if [ -z $NODES ]; then
        NODES="iln0${var}.stanford.edu:ppn=${PPN}"
    else
        NODES="${NODES}+iln0${var}.stanford.edu:ppn=${PPN}"
    fi
done

echo ${NODES}

qsub ${NODES}
