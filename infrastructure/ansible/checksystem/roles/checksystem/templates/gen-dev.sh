#!/bin/bash

for i in `seq 201 240`
do
    echo "    {name => 'team$i', network => '10.70.0.$i/32', host => '10.70.0.$i'},"
done

