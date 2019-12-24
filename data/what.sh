#!/bin/bash


while read line; do 
    echo $line | cut -d '=' -f 1
done < craigs_links.txt
