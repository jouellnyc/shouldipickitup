#!/usr/bin/env python3
#http://federalgovernmentzipcodes.us/download.html

import re
import csv
from pymemcache.client import base

zip_code_file = ('/home/john/gitrepos/shouldipickitup/' +
                 'free-zipcode-database-Primary.'       +
                 'no.header.csv')
zip_code_file = ('./free-zipcode-database-Primary.no.header.csv')

def csv_handler(zip_code_file):
    ''' Return a dictionary with zip : city,state tuples '''
    with open(zip_code_file) as csv_fh: 
        
        csv_reader = csv.reader(csv_fh, delimiter=',') 
        myzips = {} 
        
        for row in csv_reader: 
            zip   = row[0] 
            city  = row[2] 
            state = row[3] 
            myzips[zip] = (city,state) 

    return myzips


def lookup_craigs_urls(zip):
    ''' Given a zipcode and the zipcode dictionary return closest city,state ''' 
    ''' as a tuple. If no hit, find the closest and cache that in memcached  '''
    client = base.Client(('localhost', 11211))
    closest = client.get(zip)
    #No hit
    if closest is None:
        #Create zip db via file
        myzips  = csv_handler(zip_code_file)
        print('file')
        closest = myzips[min(myzips.keys(), key=lambda k: abs(int(k)-int(zip)))]
        city, state = closest
        #Add the nearest city,zip to the fast memcached cache
        client.set(zip,(city,state))
        #print(zip,(city,state))
        return (city,state)
    #Hit!
    else: 
        city, state = closest.decode("utf-8").split(',')
        patt  = re.compile('\w+')
        city  = patt.search(city).group()
        state = patt.search(state).group()
        return (city,state) 

def load_zips_to_memcached(dict):
    client = base.Client(('localhost', 11211))
    for key,value in dict.items():
        client.set(key,value)

if __name__ == "__main__":
    zipdict = csv_handler(zip_code_file)
    load_zips_to_memcached(zipdict)
