#!/bin/bash

cd lib
./craigzipsandurls.py load_mem
#This takes 29 mins! Let's make it faster! 
./govzipsandcities.py  load
