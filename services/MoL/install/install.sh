#!/bin/bash
set -e

cd ructfe-mol
rm -rf ructfe/mol/*
mkdir -p ructfe/mol
cp -r ../../service/* ructfe/mol/
rm -f ructfe/mol/static/ws.js

md5deep -l -r lib ructfe > DEBIAN/md5sums

cd ..
fakeroot dpkg-deb --build ructfe-mol
