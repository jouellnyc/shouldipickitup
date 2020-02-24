#!/bin/bash

service docker start
service nginx start
service mongodb start
/usr/local/bin/gunicorn -w 4 --bind=0.0.0.0:8000 --log-level=debug app:app --access-logfile access.log &
