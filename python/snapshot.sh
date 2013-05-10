#!/bin/sh

# Runs on supervisor machine and renames a given folder to another.
# copy rake into python/

STEP = $1
LFS = "/lfs/local/0/${USER}"
rake dsh["cp -r $LFS/supervisors $LFS/snapshot-$STEP"]
echo "Done Snapshotting $STEP"
