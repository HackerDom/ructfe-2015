#!/bin/bash

systemctl daemon-reload
systemctl enable bank
systemctl start bank

ln -s /etc/nginx/sites-available/bank /etc/nginx/sites-enabled/bank

mkdir -p /home/bank/logs
chown bank:bank -R /home/bank/
chmod 660 -R /home/bank/
find /home/bank -type d -exec chmod 770 {} +
chmod +rx /home/bank
chown -R bank:www-data /home/bank/static

service nginx restart

chmod +x /home/bank/bank_httpd
chmod +x /home/bank/*.cgi
