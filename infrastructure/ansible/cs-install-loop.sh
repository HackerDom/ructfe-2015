#!/bin/bash
while [ 1 ];
do
    echo " *** Started at: "`date`
    ./cs-install.sh
    echo " *** Finished at: "`date`
    sleep 180
done

