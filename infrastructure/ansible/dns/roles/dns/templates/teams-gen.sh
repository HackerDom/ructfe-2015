#!/bin/bash

for i in `seq 1 511`
do
    IP="10.$((60+$i/256)).$(($i%256)).2"
    printf "team%-3s           IN      A       %s\n" $i $IP
    printf "*.team%-3s         IN      A       %s\n" $i $IP
done

