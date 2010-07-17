#!/bin/bash
while true
do
    kill  $(ps ax | awk '/firelet.py/ {print $1}') 2>/dev/null
    find . -name '*pyc' -delete;
    echo -e '\n\n\n\n'
    clear
    nosetests -x test.py
    inotifywait -e MOVE_SELF *.py lib/*.py 2>/dev/null
done
