#!/usr/bin/env python3

#http://federalgovernmentzipcodes.us/download.html

import csv

''' 
Return a dictionary of key: "zip codes" and value: (city,state) tuple
'''

zip_code_file = ('/home/john/gitrepos/shouldipickitup/' +
                 'free-zipcode-database-Primary.'       +
                 'no.header.csv')

def csv_handler():
    with open(zip_code_file) as csv_fh: 
        
        csv_reader = csv.reader(csv_fh, delimiter=',') 
        myzips = {} 
        
        for row in csv_reader: 
            zip   = row[0] 
            city  = row[2] 
            state = row[3] 
            myzips[zip] = (city,state) 

    return myzips


def lookup_craigs_urls(zip,myzips):
    ''' Given a zipcode and the zipcode dictionary return the closes city'''
    return myzips.get(zip) or myzips[min(myzips.keys(), key=lambda k: abs(int(k)-int(zip)))]

