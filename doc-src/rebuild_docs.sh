#!/bin/sh
make html && \
rm ../doc/* -rf && \
mv  build/html/* ../doc/ && \
make clean && \
echo done

