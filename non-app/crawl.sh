#!/bin/bash

while read line; do ./lib/crawler.py $line; sleep 5; done < urls 
