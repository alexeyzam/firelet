#!/bin/bash

D=$(mktemp -d)

while true
    do
    /bin/cp test/*.csv "$D"
    /bin/cp test/*.json "$D"
    /bin/cp firelet.ini "$D"/
    ./firelet/daemon.py -d --cf "$D"/firelet.ini --repodir "$D"
    sleep 1
done

rm -rf "$D"
