#!/bin/bash

sudo rm repodir/demo -rf
sudo mkdir -p repodir/demo
sudo chmod a+rw repodir/demo
while true; do
 /bin/cp demo/*.csv repodir/demo/
 /bin/cp demo/*.json repodir/demo/
 ./firelet/daemon.py -D
 sleep 1
done
