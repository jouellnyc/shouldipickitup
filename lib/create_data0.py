#!/home/john/anaconda3/bin/python3.7

import os
import re
import csv
import sys

import json
from pymongo import MongoClient

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

def lookup_city_state_given_zip(zip, city_state_zips):
    ''' Given a zipcode;  return closest city,state zipcode dictionary file '''
    try:
        closest = city_state_zips[min(city_state_zips.keys(), key=lambda k: abs(int(k)-int(zip)))]
        return closest
    except TypeError as e:
        raise ValueError(e)

def create_craigs_url_dict_from_local_file(craigs_links_file):
    with open(craigs_links_file) as fh:
        contents = fh.readlines()
        craigs_city_links = {}
        for line in contents:
            citytext , craigs_link = line.split("=")
            craigs_link = ''.join(craigs_link.split())
            craigs_city_links[citytext] = craigs_link
    return craigs_city_links

def lookup_craigs_url_given_city(citytext, craigs_city_links):
    try:
        #print(citytext)
        #return craigs_city_links[citytext]
        #print(craigs_city_links[citytext])
        url = craigs_city_links[citytext]
    except KeyError as e:
        #print(e)
        #raise ValueError('no data')
        raise KeyError
        (e)

def generate_documents_to_import_to_mongodb(craigs_city_links, city_state_zips):

    print('Astatrt')
    closest_city_state = []
    for zip in ("%.5d" % x for x in range(22222,23339)):
        print(zip)
        city, state       = lookup_city_state_given_zip(zip, city_state_zips)
        citytext          = city + ',' + state
        print("I", citytext)
        #print(lookup_craigs_url_given_city(citytext, craigs_city_links))
        try:
            #print("lookup_craigs_url_given_city", citytext, "craigs_city_links")
            url               = lookup_craigs_url_given_city(citytext, craigs_city_links)
            #print(url)
        except Exception as e:
            url = None
            print("P", e)

        x = {'zip': zip, 'Details': {'City': city, 'State': state},
        'craigs_local_url' : url}
        print("x", x)
        closest_city_state.append(x)
    return closest_city_state

def load_zips_to_mongodb(closest_list):
    ''' write all the key/values to mongodb '''
    client = MongoClient()
    db = client.posts
    posts = db.posts
    new_result = posts.insert_many(closest_list)
    print('Multiple posts: {0}'.format(new_result.inserted_ids))

if __name__ == "__main__":

    import sys

    try:
        zip = sys.argv[1]
        city_state_zips    =  create_zips_city_state_dict_from_local_file(zip_code_file)
        #print(city_state_zips)
        city, state = lookup_city_state_given_zip(zip, city_state_zips)
        print("city, state:", city, state)
        citytext = city + ',' + state
        print("citytext:", citytext)
        craigs_city_links  =  create_craigs_url_dict_from_local_file(craigs_links_file)
        print('hi there')
        #print(craigs_city_links)
        try:
            craigs_url = lookup_craigs_url_given_city(citytext, craigs_city_links)
        except KeyError as e:
            print(e)
        print('5his')
        #print("E",craigs_url)
        generate_documents_to_import_to_mongodb(craigs_city_links, city_state_zips)
    except Exception as e:
        print(e)
