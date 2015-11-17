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

chown tax:tax -R /home/tax/
chmod 400 -R /home/tax/
chmod 600 -R /home/tax/data
find /home/tax -type d -exec chmod 770 {} +

service nginx restart
