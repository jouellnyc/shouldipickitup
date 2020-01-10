#!/bin/bash

while read line; do 

    ../lib/crawler.py $line index; sleep 10; 

done < <(head urls)

