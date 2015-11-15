#!/bin/bash -x

echo "CREATE USER 'nasarasa'@'localhost' IDENTIFIED BY '2ueOVgi6CCRJh8hbA5PR';" | mysql
echo "GRANT ALL PRIVILEGES ON * . * TO 'nasarasa'@'localhost';" | mysql
echo "CREATE DATABASE IF NOT EXISTS nasarasa;" | mysql

service php5-fpm stop
service nginx stop

ln -s /etc/nginx/sites-available/nasarasa /etc/nginx/sites-enabled/nasarasa

cd /usr/src
curl -sS https://getcomposer.org/installer | php
mv composer.phar /usr/bin/composer

pushd /home/nasarasa/www
composer update
popd

gpasswd -a nasarasa www-data

chown nasarasa:www-data -R /home/nasarasa/www
chmod 660 -R /home/nasarasa/www
find /home/nasarasa -type d -exec chmod 770 {} +

service php5-fpm start
service nginx start
