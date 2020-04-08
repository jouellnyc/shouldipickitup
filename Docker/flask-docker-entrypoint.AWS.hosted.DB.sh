#!/bin/bash
cd /shouldipickitup/
/usr/local/bin/gunicorn should_flask:app  -c /shouldipickitup/external/gunicorn/gunicorn.conf.py 
