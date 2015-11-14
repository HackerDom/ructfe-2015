#!/usr/bin/python3

import os
import sys

N = 512

CLIENT_DATA = """mode p2p
dev game
dev-type tun
remote vpn1.e.ructf.org {0}
remote vpn2.e.ructf.org {0}
#remote-random-hostname
ifconfig 10.{1}.{2}.2 10.{1}.{2}.1
route 10.60.0.0 255.252.0.0
route 10.80.0.0 255.252.0.0
route 10.10.10.0 255.255.255.0
keepalive 10 30
nobind
verb 3

tun-mtu 1500
fragment 1300
mssfix

<secret>
{3}
</secret>
"""

if __name__ != "__main__":
    print("I am not a module")
    sys.exit(0)

# gen client configs
os.chdir(os.path.dirname(os.path.realpath(__file__)))
try:
    os.mkdir("client")
except FileExistsError:
    print("Remove ./client dir first")
    sys.exit(1)

for i in range(1,N):
    key = open("keys/%d.key" % i).read()

    data = CLIENT_DATA.format(30000+i, 80 + i // 256, i % 256, key)
    open("client/%d.conf" % i, "w").write(data)

print("Finished, check ./client dir")
