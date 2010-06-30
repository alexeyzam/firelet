#!/bin/bash
while true
do
    inotifywait -e MOVE_SELF *.py lib/*.py test/tests.py 2>/dev/null
    kill  $(ps ax | awk '/firelet.py/ {print $1}') 2>/dev/null
    find . -name '*pyc' -delete;
    echo -e '\n======================================================================\n'
    nosetests test/tests.py
done
