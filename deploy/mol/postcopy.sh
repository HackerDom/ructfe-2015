#!/bin/bash -x

dpkg -i /root/mol/ructfe-mol.deb
rm /root/mol/ructfe-mol.deb

ln -s /etc/nginx/sites-available/mol /etc/nginx/sites-enabled/mol
service nginx restart
