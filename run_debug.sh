#!/bin/bash

while true; do
 /bin/cp test/*.csv /var/lib/firelet/
 /bin/cp test/*.json /var/lib/firelet/
 ./firelet/daemon.py -D 
 sleep 1
done
