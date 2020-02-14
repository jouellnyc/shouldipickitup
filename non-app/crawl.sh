#!/bin/bash

while read line; do 

    echo == $line ==
    date
    SLEEP=$((1 + RANDOM % 30))
    ../lib/crawler.py $line index; sleep $SLEEP; 

done < <(head -n 5 urls)
#done < urls 

