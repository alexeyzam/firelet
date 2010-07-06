#!/bin/bash

while true; do
 /bin/cp test/*.csv firewall/
 /bin/cp test/*.json firewall/
 ./firelet.py -D 
 sleep 1
done
