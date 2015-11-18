#!/bin/bash
set -e

cd mol
rm -rf home/mol/*
mkdir -p home/mol
cp -r ../../service/* home/mol/
rm -f home/mol/static/ws.js

md5deep -l -r lib home > DEBIAN/md5sums

cd ..
fakeroot dpkg-deb --build mol
