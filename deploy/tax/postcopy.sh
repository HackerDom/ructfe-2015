#!/bin/bash -x

USERNAME="tax"

pushd '/home/tax'

curl -sL https://deb.nodesource.com/setup_4.x | bash -
apt-get install -y nodejs

npm install

popd

systemctl daemon-reload
systemctl enable tax
systemctl start tax

ln -s /etc/nginx/sites-available/tax /etc/nginx/sites-enabled/tax

service nginx restart
