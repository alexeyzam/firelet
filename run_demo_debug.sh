#!/bin/bash

# Run Firelet in Demo mode (with Debug mode enabled as well)
# in a temporary directory. The iptables-save-* and
# ip-addr-show-* are used to simulate the firewalls


while true; do
    D=$(mktemp -d)
    /bin/cp tests/data/*.csv "$D"
    /bin/cp tests/data/*.json "$D"
    /bin/cp tests/data/iptables-save-* "$D"
    /bin/cp tests/data/ip-addr-show-* "$D"
    /bin/cp firelet_demo.ini "$D"/
    ./firelet/fireletd.py -d --cf "$D"/firelet_demo.ini --repodir "$D"
    rm -rf "$D"
    sleep 1
done

