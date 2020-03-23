#!/bin/bash

yum update -y
yum -y install git
yum -y install awslogs

amazon-linux-extras install docker
amazon-linux-extras enable python3
yum install python3 --disablerepo amzn2-core -y
pip3 install boto3

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install boto3

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
git clone https://github.com/jouellnyc/AWS.git 
cd AWS
source shared_vars.txt
cd boto3
chmod 755 getSecret.py
while read -r mongousername mongopassword mongohost; do 
   export MONGOUSERNAME=$mongousername export MONGOPASSWORD=$mongopassword export MONGOHOST=$mongohost
done <   <(./getSecret.py)
cd ../..
cd shouldipickitup
sed -i s"/MONGOUSERNAME/${MONGOUSERNAME}/" lib/mongodb.py 
sed -i s"/MONGOPASSWORD/${MONGOPASSWORD}/" lib/mongodb.py 
sed -i         s"/MONGOHOST/${MONGOHOST}/" lib/mongodb.py 
docker-compose -f docker-compose.AWS.hosted.MongoDb.yaml up -d
