#!/bin/bash
if [ -z $1 ]
then
    echo "Please specify: -e mode=(start|stop|startweb|stopweb|resetdb)"
    exit 1
fi
ansible-playbook cs-control/playbook.yml $@
