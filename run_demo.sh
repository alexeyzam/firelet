#!/bin/bash

while true; do
 git pull
 /bin/cp test/*.csv firewall/
 /bin/cp test/*.json firewall/
 ./firelet.py
 sleep 1
done
