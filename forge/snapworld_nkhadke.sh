#!/bin/bash

export SNAPWBIN=${HOME}/Documents/Work/Python/snapw/work-snapw
export SNAPWEXEC=${HOME}/Documents/Work/Python/snapw/work-snapw
export SNAPWOUTPUT=${HOME}/Documents/Work/Python/snapw/work-snapw/out
export PYTHON=python

# Approach for 2 nodes
SNAPWID=$1
SNAPWPORT=$2
SNAPWMASTER=$3
SNAPWMASTERPORT=$4

#SNAPWMASTER=$1
#SNAPWMASTERPORT=$2
#SNAPWID=$3
#SNAPWPORT=$4
#echo "Master Node Info"
#echo $SNAPWMASTER $SNAPWMASTERPORT

# Bash iteration on array works in reverse. Takes in arguments as:
# <master> <master port> <host> <host port> <host2> <host2 port>
# and spawns the appropriate jobs.
#i=0
#for arg in ${BASH_ARGV[*]} ; do
#    let "mod_check = $i % 2"
#    if [ $mod_check -eq 0 ]
#    then
#	SNAPWPORT=$arg
#    else
#	SNAPWID=$arg
#	if [ "$SNAPWPORT" != "$SNAPWMASTERPORT" ]
#	then
#	    echo "Host Node Info"
#	    echo $SNAPWID $SNAPWPORT
#	    echo ${PYTHON} ${SNAPWBIN}/host.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT}
#	    ${PYTHON} ${SNAPWBIN}/host.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT} >> ${SNAPWEXEC}/log-snapw-host-${SNAPWPORT}.txt 2>&1
#	fi
#    fi
#    let "i += 1"
# done

# Approach for 2 nodes
 echo $SNAPREMOTE $SNAPWID $SNAPWPORT $SNAPWMASTER $SNAPWMASTERPORT
 echo ${PYTHON} ${SNAPWBIN}/host.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT}
 ${PYTHON} ${SNAPWBIN}/host.py -d -i ${SNAPWID} -p ${SNAPWPORT} -m ${SNAPWMASTER}:${SNAPWMASTERPORT} >> ${SNAPWEXEC}/log-snapw-host-${SNAPWPORT}.txt 2>&1

#SNAPWBIN=/home/rok/git/rok/snapworld
#SNAPWEXEC=/home/rok/snapwexec
#python2.6 /lfs/1/tmp/rok/snapworld/host.py -d -i %s -p %s -m %s:%s

