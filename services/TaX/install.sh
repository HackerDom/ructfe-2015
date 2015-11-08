#!/usr/bin/env bash

CURRENT_USER_ID=$(id -u)
USERNAME="tax"

cd -P -- "$(dirname -- "$0")"

[ $(CURRENT_USER_ID) = 0 ] || (echo '[ERROR] Required `root` user access (use: `sudo install.sh`)' && exit 1)

egrep -i "^${USERNAME}" /etc/passwd > /dev/null || useradd --system ${USERNAME}

curl -sL https://deb.nodesource.com/setup_4.x | bash -
apt-get install -y nodejs
apt-get install -y npm

npm install

chown -R root:root
chown -R ${USERNAME}:${USERNAME} ./data
chown ${USERNAME}:${USERNAME} *.db
