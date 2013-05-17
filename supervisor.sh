#!/bin/bash

SNAPWID=$1
SNAPWPORT=$2
SNAPWMASTER=$3
SNAPWMASTERPORT=$4

# NOTE: no trailing / for directories
HOMELOCAL=/lfs/local/0/${USER}/supervisors/${SNAPWPORT}
export SNAPWBIN=${HOMELOCAL}/bin
export SNAPWEXEC=${HOMELOCAL}/execute
export SNAPWOUTPUT=${HOMELOCAL}/output

export PYTHON=python

mkdir -p $SNAPWBIN
mkdir -p $SNAPWEXEC
mkdir -p $SNAPWOUTPUT

###############
SRC=~/hanworks
if [ -d  "$SRC" ]; then
    fs flushvolume -path ${SRC}
    cp ${SRC}/snapworld/python/* ${SNAPWBIN}
    # cp -p ${SRC}/snap-python/swig-sw/_snap.so ${SRC}/snap-python/swig-sw/snap.py ${SNAPWBIN}
    echo "Provisioning SNAPWBIN"
else
    echo "Not provisioning SNAPWBIN via AFS"
fi
###############


echo $SNAPWID $SNAPWPORT $SNAPWMASTER $SNAPWMASTERPORT
echo ${PYTHON} ${SNAPWBIN}/supervisor.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT}
${PYTHON} ${SNAPWBIN}/supervisor.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT} >> ${SNAPWEXEC}/supervisor-sh-${SNAPWPORT}.log 2>&1

