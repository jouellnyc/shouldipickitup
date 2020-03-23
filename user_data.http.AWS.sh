#!/bin/bash

yum update -y
yum -y install git
git clone https://github.com/jouellnyc/shouldipickitup.git 
./shouldipickitup/init.sh
