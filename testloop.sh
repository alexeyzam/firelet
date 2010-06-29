#!/bin/bash
while true
do
    inotifywait firelet.py test/tests.py
    echo -e '\n======================================================================\n'
    nosetests test/tests.py
done
