#!/bin/bash

pushd '/home/hm/server'

GOPATH=/home/hm/server go get
GOPATH=/home/hm/server go build

popd

systemctl daemon-reload
systemctl enable hm
systemctl start hm
