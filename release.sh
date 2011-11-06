#!/bin/bash

set -x
set -u

# Extract version

V=$(python -c 'from firelet.flcore import __version__ as v; print v')

echo "Press enter to release v. $V"
read

# Based on the __version__ value in flcore.py , build:

#tar.gz source:
python setup.py sdist

# binary rpm
# binary tar.gz
python setup.py bdist --formats=gztar,rpm

# Debian packaging
cp dist/firelet-"$V".tar.gz ../packaging/tarballs/firelet_"$V".orig.tar.gz
ODIR=$(pwd)
cd ../packaging/firelet
git-import-orig ../tarballs/firelet_"$V".orig.tar.gz
dch -v $V-1
git commit -a -m "New upstream release: $V"
git-b

cd $ODIR




