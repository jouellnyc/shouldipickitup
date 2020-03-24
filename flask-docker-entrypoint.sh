#!/bin/bash

cd /tmp/
git clone https://github.com/jouellnyc/AWS.git
cd AWS/boto3

while read -r mongousername mongopassword mongohost; do
   export MONGOUSERNAME=$mongousername  MONGOPASSWORD=$mongopassword MONGOHOST=$mongohost
done <   <(/usr/local/bin/python3 ./getSecret.py)

cd /shouldipickitup/lib/
sed -i s"/MONGOUSERNAME/${MONGOUSERNAME}/" mongodb.py
sed -i s"/MONGOPASSWORD/${MONGOPASSWORD}/" mongodb.py
sed -i         s"/MONGOHOST/${MONGOHOST}/" mongodb.py

./create_data.py && touch create_data.done

cd /shouldipickitup/
/usr/local/bin/gunicorn -b 0.0.0.0:8000 app:app -w 4 --access-logfile access.log
