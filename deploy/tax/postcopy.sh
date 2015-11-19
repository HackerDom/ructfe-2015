#!/bin/bash -x

USERNAME="tax"

pushd '/home/tax'

curl -sL https://deb.nodesource.com/setup_4.x | bash -
DEBIAN_FRONTEND=noninteractive apt-get install -y -q --force-yes nodejs

npm install

popd

systemctl daemon-reload
systemctl enable tax
systemctl start tax

ln -s /etc/nginx/sites-available/tax /etc/nginx/sites-enabled/tax

chown tax:tax -R /home/tax/
chmod 400 -R /home/tax/
chmod 600 -R /home/tax/data
chown tax:www-data -R /home/tax/static
chmod 440 -R /home/tax/static
chmod +rx /home/tax
find /home/tax -type d -exec chmod 770 {} +

service nginx restart
