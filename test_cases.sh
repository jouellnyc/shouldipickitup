#!/bin/bash

SLEEP=2
echo "Default"
curl -s -I -X GET http://dev2.shouldipickitup.com/search/?zip=11218 | grep 200
sleep $SLEEP
echo "2 params"
curl -s -I -X GET http://dev2.shouldipickitup.com/search/?zip=11212\&hello=i | grep 200
sleep $SLEEP
echo "short zip"
curl -s -I -X GET http://dev2.shouldipickitup.com/search/?zip=1121 | grep 200
echo "text vs int"
sleep $SLEEP
curl -s -I -X GET http://dev2.shouldipickitup.com/search/?zip=mickeymouse | grep 200


<< 'MULTILINE-COMMENT'
Flask App will log before gunicorn:

INFO:should_flask:querystring: ImmutableMultiDict([('zip', '11218')])
172.18.0.4 - - [17/Apr/2020:02:04:11 +0000] "GET /search/?zip=11218 HTTP/1.0" 200 7392 "-" "curl/7.67.0" "-"
INFO:should_flask:querystring: ImmutableMultiDict([('zip', '11212'), ('hello', 'i')])
172.18.0.4 - - [17/Apr/2020:02:04:13 +0000] "GET /search/?zip=11212&hello=i HTTP/1.0" 200 7392 "-" "curl/7.67.0" "-"
ERROR:root:Invalid data: ImmutableMultiDict([('zip', '1121')]) : nota5digitzip
172.18.0.4 - - [17/Apr/2020:02:04:15 +0000] "GET /search/?zip=1121 HTTP/1.0" 200 1374 "-" "curl/7.67.0" "-"
ERROR:root:Invalid data: ImmutableMultiDict([('zip', 'mickeymouse')]) : nota5digitzip
172.18.0.4 - - [17/Apr/2020:02:04:17 +0000] "GET /search/?zip=mickeymouse HTTP/1.0" 200 1374 "-" "curl/7.67.0" "-"
MULTILINE-COMMENT
