#!/bin/bash -x

systemctl daemon-reload
systemctl enable mig
systemctl start mig

ln -s /etc/nginx/sites-available/mig /etc/nginx/sites-enabled/mig

chown mig:mig -R /home/mig/
chmod 660 -R /home/mig/
find /home/mig -type d -exec chmod 770 {} +

service nginx restart


