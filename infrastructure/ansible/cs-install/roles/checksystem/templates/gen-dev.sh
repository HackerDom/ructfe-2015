#!/bin/bash

for i in `seq 151 200`
do
    echo "    {name => 'g1 team$i', network => '10.70.0.$i/32', host => 'dev$i.e.ructf.org'},"
done

for i in `seq 151 200`
do
    echo "    {name => 'g7 team$i', network => '10.70.1.$i/32', host => 'devnew$i.e.ructf.org'},"
done

for i in `seq 491 510`
do
    IP="10.$((60+$i/256)).$(($i%256)).0/24"
    echo "    {name => 'ProdVPN team$i', network => '$IP', host => 'team$i.e.ructf.org'},"
done
