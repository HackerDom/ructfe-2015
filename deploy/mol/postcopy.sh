#!/bin/bash -x

dpkg -i /root/mol/mol.deb
rm /root/mol/mol.deb

ln -s /etc/nginx/sites-available/mol /etc/nginx/sites-enabled/mol
service nginx restart
