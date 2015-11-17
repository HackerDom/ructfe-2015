#!/bin/bash -x

VBoxManage controlvm team$1-x64 poweroff
VBoxManage unregistervm team$1-x64 --delete

