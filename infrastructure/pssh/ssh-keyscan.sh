#!/bin/bash
for f in servers-full servers-short
do
	ssh-keyscan -f $f
done
