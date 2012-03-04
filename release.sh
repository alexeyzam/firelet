#!/bin/bash

set -x
set -u

PACKAGING_DIR=~/projects/packaging/firelet
PACKAGING_OUT_DIR=~/projects/packaging/build-area

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
cd $PACKAGING_DIR
git-import-orig ../tarballs/firelet_"$V".orig.tar.gz
dch -v $V-1 -r experimental 'New upstream release'
git commit -a -m "New upstream release: $V"
git-buildpackage --git-ignore-new

echo "Install .deb package locally [y/n]?"
read ANS
if ["$ANS" == 'y'] then
    cd $PACKAGING_OUT_DIR
    sudo dpkg -i firelet_$V-1_all.deb
fi

cd $ODIR




