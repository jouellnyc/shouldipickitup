#!/home/john/anaconda3/bin/python3.7

import os
import sys
import logging

import csv
import statistics
from collections import defaultdict


'''
===============================================
Zip code, City, State, Craigslist Url strategy:
===============================================


#Round 1

Take 2 files:

free-zipcode-database-Primary.no.header.csv - zip codes to City, State
craigs_links.txt - City, State names to Craigslist City zips2knowncityurls

Then create 2 dictionaries:

#Zip to city state
11111-> boston ma

and

#city, state to craigslist url
boston,ma -> link.craig.com

#Set up a table from those 2 dictionaries with details:

{'zip': '49831', 'City': 'Felch', 'State': 'MI', 'craigs_local_url': "blah.com"}
{'zip': '49832', 'City': 'Felch', 'State': 'MI', 'craigs_local_url':  None}
...

#Round 2
#Then get the closest zip to the  known zips (fill in the Nones) using a 3rd dictionary

#This is still imperfect data, but at least all of the zip in the government
#file will have relevant data from somewhere 'somewhat' close.
#This also means Brooklyn could be considered close to Albany...(well, kind of, for now)

#Round 3
Set craigs_url as the key and insert all the associated zip as values in the same
document. Query for a member of the array to get the items.

#Round 4
Find out all the other mappings w/o commas and load those.
Load PR and any other remote sites
'''

URL = 'http://federalgovernmentzipcodes.us/download.html'  # not used
my_file_name = os.path.basename(__file__)
zip_code_file = '/home/john/gitrepos/shouldipickitup/data/free-zipcode-database-Primary.no.header.csv'
craigs_links_file = '/home/john/gitrepos/shouldipickitup/data/craigs_links.txt'

def create_govcity_state_zips_dict_from_local_file(zip_code_file):
    ''' Return a dictionary with (city,state) zip values    '''
    ''' give the file at URL                                '''
    gov_city_state_zips = defaultdict(list)
    with open(zip_code_file) as csv_fh:
        csv_reader = csv.reader(csv_fh, delimiter=',')
        for row in csv_reader:
            zipc = row[0]
            city = row[2]
            city = city.lower()
            city = " ".join(city.split())  # no spaces
            state = row[3]
            state = " ".join(state.split())
            state = state.upper()
            gov_city_state_zips[f"{city},{state}"].append(zipc)
        return gov_city_state_zips

def create_craigs_url_dict_from_local_file(craigs_links_file):
    ''' Return a dictionary (city,state => url)             '''
    ''' give the craigs_links_file file                     '''
    with open(craigs_links_file) as fh:
        contents = fh.readlines()
        craigs_city_links = {}
        for line in contents:
            citytext, craigs_link = line.split("=")
            craigs_link = ''.join(craigs_link.split())
            craigs_city_links[citytext] = craigs_link

    return craigs_city_links


def lookup_craigs_url_with_city(citystate, craigs_city_links):
    return craigs_city_links[citystate]

def create_zipcode_2_craigs_url_map(craigs_city_links, gov_city_state_zips):
    ''' return the mean of the zips associated with a craigsurl '''
    mean_zip2craigs_url = {}

    for citystate, ziplist in gov_city_state_zips.items():
        try:
            ziplist = [ int(x) for x in ziplist ]
            craigs_url = lookup_craigs_url_with_city(citystate, craigs_city_links)
            mean = round(statistics.median(ziplist))
            if len(str(mean)) == 4:
                mean = str(0) + str(mean)
            mean_zip2craigs_url[mean] = craigs_url
        except KeyError:
            pass #don't care about these at all

    return mean_zip2craigs_url


def find_closest_craigs_url_for_other_cities(zip, mean_zip2craigs_url):
   ''' Given a zipcode;  return URL of a zip with a known Craigslist URL '''

   if zip[0] == 0:
       zip = zip[1:]
   try:
       closest = mean_zip2craigs_url[min(mean_zip2craigs_url.keys(), key=lambda k: abs(int(k)-int(zip)))]
       return closest
   except TypeError as e:
       raise ValueError(e)


def generate_master_documents_import_to_mongodb(
    craigs_city_links, gov_city_state_zips, mean_zip2craigs_url):

    print(" == hi == ")
    master_mongo_city_state_zip_map = {}
    print(" == h2 == ")

    for citystate, ziplist in gov_city_state_zips.items():
        try:
            print("============================================================hi3=============" , citystate)
            url = lookup_craigs_url_with_city(citystate, craigs_city_links)
            print(url)
            master_mongo_city_state_zip_map[url]               = {}
            master_mongo_city_state_zip_map[url]['CityState']  = citystate
            master_mongo_city_state_zip_map[url]['Zips']       = ziplist
            master_mongo_city_state_zip_map[url]['AltZips']    = []
            master_mongo_city_state_zip_map[url]['AltCities']  = []
        except KeyError as e:
            #   print("e ",e)
            try:
                print("hi4", citystate)
                first_zip = ziplist[0] # so ugly to have a bare '0'
                print("first zip: ", first_zip)
                url = find_closest_craigs_url_for_other_cities(first_zip, mean_zip2craigs_url)
            except Exception as e:
                print("hi================================================= ", e)
            else:
                print("Good here ", url)
                try:
                    # print("ziplist: ", ziplist)
                    #print("mm: ", master_mongo_city_state_zip_map[url]['AltZips'])
                    print("trying")
                    master_mongo_city_state_zip_map[url]['AltZips'].append(ziplist)
                except Exception as e:
                    logging.exception('Caught an error')
                    print("here:", e)
                #print(master_mongo_city_state_zip_map[url]['AltZips'])
                #master_mongo_city_state_zip_map[url]['AltCities'].append(citystate)
                #print(master_mongo_city_state_zip_map[url]['AltCities'])

    #for k, v in master_mongo_city_state_zip_map.items():
    #    print(k, v)
    #return master_mongo_city_state_zip_map

if __name__ == "__main__":

    try:
        #Round 3
        craigs_city_links        = create_craigs_url_dict_from_local_file(craigs_links_file)
        gov_city_state_zips      = create_govcity_state_zips_dict_from_local_file(zip_code_file)
        mean_zip2craigs_url      = create_zipcode_2_craigs_url_map(craigs_city_links, gov_city_state_zips)
        #print(mean_zip2craigs_url)
        generate_master_documents_import_to_mongodb(craigs_city_links, gov_city_state_zips, mean_zip2craigs_url)
        #mongodb.init_load_city_state_zip_map(mongo_city_state_zip_map)
        # This takes about 10 seconds now!
    except Exception as e:
        print("Error: ", e)
