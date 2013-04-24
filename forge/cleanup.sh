#!/bin/bash

# A script that cleans up snapw files and kills any stray processes
echo "Killing stray processes"
ps aux | grep python | grep lfs | awk '{print $2}' | xargs kill -9
for i in 0 1 2 3 4 5 6 7 8 9
do
    echo "removing snapw.$i*"
    rm -rf snapw.$i*
done

echo "Removing text files"
rm log-snapw-host*.txt
rm log-swhost-*.txt
echo "done"