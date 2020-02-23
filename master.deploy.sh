#!/bin/bash

set -e
set -u

NETWORK="shouldinetwork"

if docker network ls | grep -i "${NETWORK}";then
	docker network rm "${NETWORK}" 
fi

docker network create --driver=bridge \
--subnet=172.18.0.0/16 \
--ip-range=172.18.0.0/24 \
--gateway=172.18.0.1 "${NETWORK}" 


function mongodb  {

APP=mongod
APP_IP="172.18.0.4"
echo "Building $APP at $APP_IP"
docker volume create mongodbdata && \
docker build -f Dockerfile."${APP}" . -t "my_${APP}:latest" 
docker run   -d --cap-drop=all --mount source=mongodbdata,target=/data/db  --network "${NETWORK}" --ip "${APP_IP}"  "my_${APP}:latest" 

}


function nginx {

APP=nginx
APP_IP="172.18.0.2"
echo "Building $APP at $APP_IP"
docker build -f Dockerfile."${APP}" . -t "my_${APP}:latest" 
#TBD:get --cap-drop tuned 
docker run   -d               -p 80:8080   --network "${NETWORK}" --ip "${APP_IP}"  "my_${APP}:latest" 

}


function flask {

APP=flask
APP_IP="172.18.0.3"
echo "Building $APP at $APP_IP"
docker build -f Dockerfile."${APP}" . -t "my_${APP}:latest" 
docker run   -d --cap-drop=all             --network "${NETWORK}" --ip "${APP_IP}"  "my_${APP}:latest" 

}

case $1 in
    "flask") flask ;;
    "nginx") nginx ;;
    "mongodb") mongodb ;;
esac

netstat -lnat | grep -iE "80|8000|27017"
docker ps 
