#!/bin/sh

PPN=20
for var in {1..9}
do
    if [ -z $NODES ]; then
        NODES="iln0${var}.stanford.edu:ppn=${PPN}"
    else
        NODES="${NODES}+iln0${var}.stanford.edu:ppn=${PPN}"
    fi
done

CMD="qsub -I -l nodes=${NODES}"

echo $CMD

$CMD
