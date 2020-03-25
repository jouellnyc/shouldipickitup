#!/bin/bash
cd /shouldipickitup/lib
./create_data.py && touch create_data.done
cd ..
/usr/local/bin/gunicorn -b 0.0.0.0:8000 app:app -w 4 --access-logfile access.log
