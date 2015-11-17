#!/bin/bash

systemctl daemon-reload
systemctl enable bank
systemctl start bank

ln -s /etc/nginx/sites-available/bank /etc/nginx/sites-enabled/bank

chown bank:bank -R /home/bank/
chmod 660 -R /home/bank/
find /home/bank -type d -exec chmod 770 {} +

service nginx restart

chmod +x /home/bank/bank_httpd/bank_httpd

