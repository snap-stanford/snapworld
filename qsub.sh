#!/bin/sh

PPN=10
for var in {1..9}
do
    if [ -z $NODES ]; then
        NODES="iln0${var}.stanford.edu:ppn=${PPN}"
    else
        NODES="${NODES}+iln0${var}.stanford.edu:ppn=${PPN}"
    fi
done

echo "qsub -I -l nodes=${NODES}"

# qsub -I -l nodes=${NODES}
