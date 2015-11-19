#!/bin/bash

for i in `seq 151 254`
do
    IP="10.70.0.$i"
    printf "dev%-3s           IN      A       %s\n" $i $IP
    printf "*.dev%-3s         IN      A       %s\n" $i $IP
done

for i in `seq 151 254`
do
    IP="10.70.1.$i"
    printf "devnew%-3s        IN      A       %s\n" $i $IP
    printf "*.devnew%-3s      IN      A       %s\n" $i $IP
done

echo

