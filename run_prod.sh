#!/bin/bash

sudo rm repodir/debug -rf
sudo mkdir -p repodir/debug
sudo chmod a+rw repodir/debug
while true; do
 /bin/cp tests/data/*.csv repodir/debug/
 /bin/cp tests/data/*.json repodir/debug/
 ./firelet/fireletd.py -D
 sleep 1
done
