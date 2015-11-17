#!/bin/bash

pushd /root/ructfe-2015/services/bank
make
cd bank_httpd
make
popd
