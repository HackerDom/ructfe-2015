#!/bin/bash -x

systemctl daemon-reload
systemctl enable mig
systemctl start mig

ln -s /etc/nginx/sites-available/mig /etc/nginx/sites-enabled/mig

sed -i 's/save 60 10000/save 60 1/' /etc/redis/redis.conf

pushd /home/mig

git clone -b master git://github.com/nim-lang/Nim.git
pushd Nim
git clone -b master --depth 1 git://github.com/nim-lang/csources
cd csources && sh build.sh && cd ..
popd

popd

chmod +x /home/mig/Nim/bin/nim
pushd /home/mig/src
/home/mig/Nim/bin/nim cc -d:release main.nim
popd

chown mig:mig -R /home/mig/
chmod 660 -R /home/mig/
find /home/mig -type d -exec chmod 770 {} +

service nginx restart


