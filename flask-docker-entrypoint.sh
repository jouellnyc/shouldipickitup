#!/bin/bash
cd /shouldipickitup/lib
./create_data.py
#cd /shouldipickitup/non-app
#./crawl.sh
cd /shouldipickitup/
/usr/local/bin/gunicorn -b 0.0.0.0:8000 app:app -w 4 --access-logfile access.log
