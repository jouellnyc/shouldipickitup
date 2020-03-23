#!/bin/bash

yum update -y
yum -y install awslogs
amazon-linux-extras install docker

curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

service docker start
chkconfig docker on
service awslogsd start
chkconfig awslogsd on

docker-compose -f docker-compose.AWS.hosted.MongoDb.yaml up -d
