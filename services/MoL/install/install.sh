#!/bin/bash
set -e

cd ructfe-mol
rm -rf ructfe/mol/*
cp -r ../../service/* ructfe/mol/
rm -f ructfe/mol/static/ws.js

md5deep -l -r lib ructfe > DEBIAN/md5sums

cd ..
echo "RUN: \`fakeroot dpkg-deb --build ructfe-mol\` at the debian system"
exit 0
#fakeroot dpkg-deb --build ructfe-mol
