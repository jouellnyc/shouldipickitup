#!/home/john/anaconda3/bin/python3.7

import os
import re
import csv
import sys

import json
from pymongo import MongoClient

'''
===============================================
Zip code, City, State, Craigslist Url strategy:
===============================================

free-zipcode-database-Primary.no.header.csv - zip codes to City, State generate_documents_to_import_to_mongodb
craigs_links.txt = City, State names to Craigslist zips2knowncityurls

#Round 1
Create 2 dictionaries:
#zip to city
11111-> boston ma

#City to craigslist url
boston,ma -> link.craig.com

#Set up a table from those 2 dictionaries with details:
{'zip': '49831', 'Details': {'City': 'felch', 'State': 'MI'}, 'craigs_local_url': "blah.com"}
{'zip': '49832', 'Details': {'City': 'felch', 'State': 'MI'}, 'craigs_local_url':     None  }

#Round 2
#Then get the closest zip to the  known zips (fill in the Nones) using a 3rd dictionary
{'zip': '49831', 'Details': {'City': 'felch', 'State': 'MI'}, 'craigs_local_url': None}

#This is still imperfect data, but at least all of the zip in the government
#file will have relevant data from somewhere 'somewhat' close.

#Round 3
Find out all the other mappings w/o commas and load those.

#Round 4
Load PR and any other remote sites

'''

URL = 'http://federalgovernmentzipcodes.us/download.html' # not used
my_file_name = os.path.basename(__file__)
zip_code_file = '/home/john/gitrepos/shouldipickitup/data/free-zipcode-database-Primary.no.header.csv'
craigs_links_file = '/home/john/gitrepos/shouldipickitup/data/craigs_links.txt'

def create_zips_city_state_dict_from_local_file(zip_code_file):
    ''' Return a dictionary with zip : (city,state) tuples  '''
    ''' give the file at URL                                '''
    with open(zip_code_file) as csv_fh:
            city_state_zips = {}
            csv_reader = csv.reader(csv_fh, delimiter=',')

            for row in csv_reader:
                zip   = row[0]
                city  = row[2]
                city  = city.lower()
                city  = "".join(city.split()) # no spaces
                state = row[3]
                state = state.upper()
                city_state_zips[zip] = (city,state)

    return city_state_zips

def create_craigs_url_dict_from_local_file(craigs_links_file):
    ''' Return a dictionary (city,state => url)             '''
    ''' give the craigs_links_file file                     '''
    with open(craigs_links_file) as fh:
        contents = fh.readlines()
        craigs_city_links = {}
        for line in contents:
            citytext , craigs_link = line.split("=")
            craigs_link = ''.join(craigs_link.split())
            craigs_city_links[citytext] = craigs_link
    return craigs_city_links

def lookup_closest_craigs_url_given_zip_with_known_link(zip, city_state_zips):
    ''' Given a zipcode;  return URL of a zip with a known Craigslist URL '''
    try:
        closest = city_state_zips[min(city_state_zips.keys(), key=lambda k: abs(int(k)-int(zip)))]
        return closest
    except TypeError as e:
        raise ValueError(e)

def lookup_craigs_url_given_city(citytext, craigs_city_links):
    return craigs_city_links[citytext]

def lookup_city_state_given_zip(zip, zip_code_dict):
    return zip_code_dict[zip]

def lookup_craigs_url_given_zip(zip, zip_code_dict):
    return zip_code_dict[zip]

def create_map_of_zips_to_known_city_urls(craigs_city_links, gov_city_state_zips):
    ''' Given the 2 mappings, combine where you can pull out a craiglist url '''
    city_state_zip_map = {}
    for zip in (gov_city_state_zips.keys()):
        city, state       = lookup_city_state_given_zip(zip, gov_city_state_zips)
        citytext          = city + ',' + state
        try:
            city_state_zip_map[zip] = craigs_city_links[citytext]
        except KeyError:
            url = None
    return city_state_zip_map

def generate_documents_to_import_to_mongodb(zips2knowncityurls, gov_city_state_zips):
    ''' Format the data for importing to Mongodb                              '''
    ''' If a url is not found, find the closest zip and use that url          '''
    city_state_zip_map = []

    for zip in (gov_city_state_zips.keys()):

        try:
            url               = lookup_craigs_url_given_zip(zip, zips2knowncityurls)
        except KeyError:
            url               = lookup_closest_craigs_url_given_zip_with_known_link(zip, zips2knowncityurls)

        city, state       = lookup_city_state_given_zip(zip, gov_city_state_zips)
        x = {'zip': zip, 'Details': {'City': city, 'State': state},'craigs_local_url' : url}
        city_state_zip_map.append(x)
        print(x)

    return city_state_zip_map

if __name__ == "__main__":

    import sys
    import mongodb

    try:
        #Round 1
        gov_city_state_zips = create_zips_city_state_dict_from_local_file(zip_code_file)
        craigs_city_links   = create_craigs_url_dict_from_local_file(craigs_links_file)
        zips2knowncityurls  = create_map_of_zips_to_known_city_urls(craigs_city_links, gov_city_state_zips)
        #Round 2
        mongo_city_state_zip_map  = generate_documents_to_import_to_mongodb(zips2knowncityurls, gov_city_state_zips)
        mongodb.load_zips_to_mongodb(mongo_city_state_zip_map)
        #This takes about 2-3 minutes
        #This also means Brooklyn could be considered close to Albany...(well, kind of, for now)
    except Exception as e:
        print(e)
