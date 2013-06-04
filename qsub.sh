#!/bin/sh

PPN=12

NODES=`seq -f "iln%02g.stanford.edu:ppn=${PPN}" -s "+" 1 21`

CMD="qsub -I -l nodes=${NODES}"

echo $CMD

$CMD
