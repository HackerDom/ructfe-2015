#!/bin/bash -x

echo "CREATE USER 'nasarasa'@'localhost' IDENTIFIED BY '2ueOVgi6CCRJh8hbA5PR';" | mysql
echo "GRANT ALL PRIVILEGES ON * . * TO 'nasarasa'@'localhost';" | mysql
echo "CREATE DATABASE IF NOT EXISTS nasarasa;" | mysql

service php5-fpm stop
service nginx stop

ln -s /etc/nginx/sites-available/nasarasa /etc/nginx/sites-enabled/nasarasa

service php5-fpm start
service nginx start
