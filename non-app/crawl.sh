#!/bin/bash

CITIES=known_cities.txt

while read line; do

    echo == $line ==
    date
    SLEEP=$((1 + RANDOM % 30))
    ../lib/crawler.py $line index; sleep $SLEEP;

done < <(head -n 5 $CITIES)
#done < $CITIES
