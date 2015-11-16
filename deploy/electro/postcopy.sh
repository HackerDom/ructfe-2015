#!/bin/bash

echo "deb http://download.mono-project.com/repo/debian wheezy main" > /etc/apt/sources.list.d/mono-xamarin.list
echo "deb http://download.mono-project.com/repo/debian wheezy-libjpeg62-compat main" >> /etc/apt/sources.list.d/mono-xamarin.list

apt-get update
apt-get install mono-devel

chown electro:electro -R /home/electro/
chmod 660 -R /home/electro/
find /home/electro -type d -exec chmod 770 {} +

systemctl daemon-reload
systemctl enable electro
systemctl start electro

ln -s /etc/nginx/sites-available/electro /etc/nginx/sites-enabled/electro

service nginx restart
