#!/bin/bash
set -e

cd ructfe-mol
rm -rf ructfe/mol/*
cp -r ../../service/* ructfe/mol/

md5deep -l -r lib ructfe > DEBIAN/md5sums

cd ..
fakeroot dpkg-deb --build ructfe-mol
