#!/bin/bash

pushd '/home/hm/server'

GOPATH=/home/hm/server go get
GOPATH=/home/hm/server go build

popd


ln -s /etc/nginx/sites-available/hm /etc/nginx/sites-enabled/hm

chown hm:hm -R /home/hm/
chmod 660 -R /home/hm/
find /home/hm -type d -exec chmod 770 {} +

service nginx restart

chmod +x /home/hm/server/server

systemctl daemon-reload
systemctl enable hm
systemctl start hm
