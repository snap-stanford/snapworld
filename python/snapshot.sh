#!/bin/sh

# Runs on supervisor machine and copies a given folder to another.
# TODO: There should be a flag in the config file (master level fix)

STEP=$1
LFS="/lfs/local/0/${USER}"
cd ../
rake dsh["cp -r $LFS/supervisors $LFS/snapshot-$STEP"]
echo "Done Snapshotting $STEP"
