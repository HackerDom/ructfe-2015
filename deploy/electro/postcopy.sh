#!/bin/bash

# apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
# echo "deb http://download.mono-project.com/repo/debian wheezy main" > /etc/apt/sources.list.d/mono-xamarin.list
# echo "deb http://download.mono-project.com/repo/debian wheezy-libjpeg62-compat main" >> /etc/apt/sources.list.d/mono-xamarin.list

# apt-get update
# DEBIAN_FRONTEND=noninteractive apt-get install -y -q --force-yes mono-devel

chown electro:www-data -R /home/electro/
chmod 660 -R /home/electro/
find /home/electro -type d -exec chmod 770 {} +

systemctl daemon-reload
systemctl enable electro
systemctl start electro

ln -s /etc/nginx/sites-available/electro /etc/nginx/sites-enabled/electro

service nginx restart
