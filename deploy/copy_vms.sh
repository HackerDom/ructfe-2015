#!/bin/bash -x

VBoxManage controlvm team$2-x64 poweroff
VBoxManage unregistervm team$2-x64 --delete
VBoxManage clonevm team$1-x64 --mode all --name team$2-x64 --register
VBoxManage startvm team$2-x64 --type headless

ping -c 10 10.70.0.$1

ssh -i /tmp/deploy-key-vbox root@10.70.0.$1 sed -i "s/$1/$2/" /etc/network/interfaces
ssh -i /tmp/deploy-key-vbox root@10.70.0.$1 /etc/init.d/networking restart &
