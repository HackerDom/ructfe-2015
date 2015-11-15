#!/bin/bash
echo "You can use: -e mode=(start|stop|restart|resetdb)"
ansible-playbook checksystem/playbook.yml $@
