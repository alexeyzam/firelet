#!/bin/bash
while true
do
    inotifywait -e MOVE_SELF *.py test/tests.py 2>/dev/null
    echo -e '\n======================================================================\n'
    nosetests test/tests.py
done
