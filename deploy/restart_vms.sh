#!/bin/bash -x

VBoxManage controlvm dirty-x64 poweroff
#VBoxManage controlvm team220-x64 poweroff
VBoxManage controlvm team222-x64 poweroff
#VBoxManage controlvm team100-x64 poweroff

sleep 3

VBoxManage snapshot dirty-x64 restore clean
#VBoxManage snapshot team220-x64 restore clean
VBoxManage snapshot team222-x64 restore clean
#VBoxManage snapshot team100-x64 restore clean

sleep 3

VBoxManage startvm dirty-x64 --type headless
#VBoxManage startvm team220-x64 --type headless
VBoxManage startvm team222-x64 --type headless
#VBoxManage startvm team100-x64 --type headless
