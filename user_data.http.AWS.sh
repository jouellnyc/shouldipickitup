#!/bin/bash

yum update -y

amazon-linux-extras install docker
yum -y install git 
yum -y install awslogs 

curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

service docker start
chkconfig docker on
service awslogsd start
chkconfig awslogsd on

GIT_DIR="/gitrepos/"
mkdir -p $GIT_DIR
cd $GIT_DIR/
git clone https://github.com/jouellnyc/shouldipickitup.git 
git clone https://github.com/jouellnyc/AWS.git 
cd AWS
source shared_vars.txt
cd boto3
chmod 755 getSecret.py
while read -r username password mongohost; do 
    MONGOUSERNAME=$username MONGOPASSWORD=$password MONGOHOST=$mongohost
done <   <(../AWS/boto3/getSecret.py)
cd ../..
cd shouldipickitup
sed -i s"/MONGOUSERNAME/${MONGOUSERNAME}/" lib/mongodb.py 
sed -i s"/MONGOPASSWORD/${MONGOPASSWORD}/" lib/mongodb.py 
sed -i         s"/MONGOHOST/${MONGOHOST}/" lib/mongodb.py 
docker-compose -f docker-compose.AWS.hosted.MongoDb.yaml up -d
