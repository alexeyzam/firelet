#!/bin/bash

D=$(mktemp -d)
echo "Using $D as temporary directory..."
while true
    do
    pkill firelet
    /bin/cp tests/data/*.csv "$D"
    /bin/cp tests/data/*.json "$D"
    /bin/cp firelet.ini "$D"/
    ./firelet/fireletd.py -d --cf "$D"/firelet.ini --repodir "$D"
    sleep 1
done

rm -rf "$D"
