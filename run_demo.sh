#!/bin/bash

# Run Firelet in Demo mode (without the Debug flag)
# in a temporary directory. The iptables-save-* and
# ip-addr-show-* are used to simulate the firewalls


while true; do
    D=$(mktemp -d)
    /bin/cp test/*.csv "$D"
    /bin/cp test/*.json "$D"
    /bin/cp test/iptables-save-* "$D"
    /bin/cp test/ip-addr-show-* "$D"
    /bin/cp firelet_demo.ini "$D"/
    ./firelet/fireletd.py --cf "$D"/firelet_demo.ini --repodir "$D"
    rm -rf "$D"
    sleep 1
done

