#!/bin/bash
git -C ../../../checksystem/ pull
git pull
ansible-playbook cs-install/playbook.yml $@
