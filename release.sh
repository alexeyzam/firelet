#!/bin/bash

set -e
set -u

PACKAGING_DIR=~/projects/packaging/firelet
PACKAGING_OUT_DIR=~/projects/packaging/build-area

function ask() {
    echo -ne "\n$1 [y/n]? "; read ANS
    [[ $ANS == "y" ]] && return 0;
    return 1;
}

# Extract version
V=$(python -c 'from firelet.flcore import __version__ as v; print v')

if ! ask "release v. $V"; then exit; fi

# Based on the __version__ value in flcore.py , build:
#tar.gz source:
python setup.py sdist

# binary rpm
# binary tar.gz
python setup.py bdist --formats=gztar,rpm

# Debian packaging
if ask "Perform Debian packaging"; then
    cp dist/firelet-"$V".tar.gz ../packaging/tarballs/firelet_"$V".orig.tar.gz
    ODIR=$(pwd)
    cd $PACKAGING_DIR
    git-import-orig ../tarballs/firelet_"$V".orig.tar.gz
    dch -v $V-1 --distribution experimental 'New upstream release'
    git commit -a -m "New upstream release: $V"
    git-buildpackage --git-ignore-new

    if ask "Install .deb package locally"; then
        cd $PACKAGING_OUT_DIR
        sudo dpkg -i firelet_$V-1_all.deb
    fi
fi




