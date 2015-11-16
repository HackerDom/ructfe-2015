#!/bin/bash

CLIENT=client
TEAMS=$CLIENT/teams
TESTCLOSE=$CLIENT/test-close
TESTOPEN=$CLIENT/test-open

for d in $TEAMS $TESTCLOSE $TESTOPEN
do
    if [ -d $d ]
    then
        rm $d/*.conf
    else
        mkdir $d
    fi
done

for i in `seq 1 490`;   do mv $CLIENT/$i.conf $TEAMS; done
for i in `seq 491 495`; do mv $CLIENT/$i.conf $TESTCLOSE; done
for i in `seq 496 511`; do mv $CLIENT/$i.conf $TESTOPEN; done
