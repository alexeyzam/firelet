#!/bin/bash

D=$(mktemp -d)
echo "Using $D as temporary directory..."
while true
    do
    pkill firelet
    /bin/cp test/*.csv "$D"
    /bin/cp test/*.json "$D"
    /bin/cp firelet.ini "$D"/
    ./firelet/fireletd.py -d --cf "$D"/firelet.ini --repodir "$D"
    sleep 1
done

rm -rf "$D"
