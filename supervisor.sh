#!/bin/bash

# NOTE: no trailing / for directories
HOMELOCAL=/lfs/local/0/${USER}/supervisor
export SNAPWBIN=${HOMELOCAL}/bin
export SNAPWEXEC=${HOMELOCAL}/execute
export SNAPWOUTPUT=${HOMELOCAL}/output

export PYTHON=python

mkdir -p $SNAPWBIN
mkdir -p $SNAPWEXEC
mkdir -p $SNAPWOUTPUT

###############
SRC=~/hanworks/snapworld/python/
if [ -d  "$SRC" ]; then
    cp ${SRC}/* $SNAPWBIN
    echo "Provisioning SNAPWBIN"
else
    echo "Not provisioning SNAPWBIN via AFS"
fi
###############

SNAPWID=$1
SNAPWPORT=$2
SNAPWMASTER=$3
SNAPWMASTERPORT=$4

echo $SNAPWID $SNAPWPORT $SNAPWMASTER $SNAPWMASTERPORT
echo ${PYTHON} ${SNAPWBIN}/host.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT}
${PYTHON} ${SNAPWBIN}/supervisor.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT} >> ${SNAPWEXEC}/log-snapw-host-${SNAPWPORT}.txt 2>&1

