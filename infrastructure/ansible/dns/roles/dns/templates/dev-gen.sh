#!/bin/bash

for i in `seq 201 254`
do
    IP="10.70.0.$i"
    printf "dev%-3s           IN      A       %s\n" $i $IP
    printf "*.dev%-3s         IN      A       %s\n" $i $IP
done
