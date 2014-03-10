#!/bin/bash

SNAPW_ID=$1
SNAPW_PORT=$2
SNAPW_MASTER=$3
SNAPW_MASTER_PORT=$4
SNAPW_BROKER_PORT=$5
SNAPW_BROKER_TOKENS=$6

# NOTE: no trailing / for directories
HOMELOCAL=/lfs/local/0/${USER}/supervisors/${SNAPW_PORT}
export SNAPW_BIN=${HOMELOCAL}/bin
export SNAPW_EXEC=${HOMELOCAL}/execute
export SNAPW_OUTPUT=${HOMELOCAL}/output

export PYTHON=python2.7

mkdir -p $SNAPW_BIN
mkdir -p $SNAPW_EXEC
mkdir -p $SNAPW_OUTPUT

###############
SRC=~/hanworks
if [ -d  "$SRC" ]; then
    fs flushvolume -path ${SRC}
    cp ${SRC}/snapworld/python/* ${SNAPW_BIN}
    cp -r ${SRC}/snapworld/broker ${SNAPW_BIN}/
    # cp -p ${SRC}/snap-python/swig-sw/_snap.so ${SRC}/snap-python/swig-sw/snap.py ${SNAPW_BIN}
    echo "Provisioning SNAPW_BIN"
else
    echo "Not provisioning SNAPW_BIN via AFS"
fi
###############

node ${SNAPW_BIN}/broker/broker.js ${SNAPW_BROKER_PORT} ${SNAPW_BROKER_TOKENS} &> ${SNAPW_OUTPUT}/broker.log &

echo $SNAPW_ID $SNAPW_PORT $SNAPW_MASTER $SNAPW_MASTER_PORT
echo ${PYTHON} ${SNAPW_BIN}/supervisor.py -d -i ${SNAPW_ID} -p ${SNAPW_PORT} -m ${SNAPW_MASTER}:${SNAPW_MASTER_PORT}
${PYTHON} ${SNAPW_BIN}/supervisor.py -d -i ${SNAPW_ID} -p ${SNAPW_PORT} -m ${SNAPW_MASTER}:${SNAPW_MASTER_PORT} >> ${SNAPW_EXEC}/supervisor-sh-${SNAPW_PORT}.log 2>&1

