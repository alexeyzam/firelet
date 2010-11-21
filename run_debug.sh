#!/bin/bash

sudo rm repodir/debug -rf
sudo mkdir -p repodir/debug
sudo chmod a+rw repodir/debug
while true; do
 /bin/cp test/*.csv repodir/debug/
 /bin/cp test/*.json repodir/debug/
 ./firelet/daemon.py -D
 sleep 1
done
