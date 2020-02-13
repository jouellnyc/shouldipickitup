#!/home/john/anaconda3/bin/python3.7

import os
import re
import csv
import sys

import json
from pymongo import MongoClient

URL = "http://federalgovernmentzipcodes.us/download.html"  # not used
my_file_name = os.path.basename(__file__)
zip_code_file = "/home/john/gitrepos/shouldipickitup/data/free-zipcode-database-Primary.no.header.csv"
craigs_links_file = "/home/john/gitrepos/shouldipickitup/data/craigs_links.txt"


def create_zips_city_state_dict_from_local_file(zip_code_file):
    """ Return a dictionary with zip : (city,state) tuples  """
    """ give the file at URL                                """
    with open(zip_code_file) as csv_fh:
        city_state_zips = {}
        csv_reader = csv.reader(csv_fh, delimiter=",")

        for row in csv_reader:
            zip = row[0]
            city = row[2]
            city = city.lower()
            city = "".join(city.split())  # no spaces
            state = row[3]
            state = state.upper()
            city_state_zips[zip] = (city, state)

    return city_state_zips


def find_closest_url_to_city_given_zip(zip, city_state_zips):
    """ Given a zipcode;  return closest city,state zipcode dictionary file """
    try:
        closest = city_state_zips[
            min(city_state_zips.keys(), key=lambda k: abs(int(k) - int(zip)))
        ]
        return closest
    except TypeError as e:
        raise ValueError(e)


def create_craigs_url_dict_from_local_file(craigs_links_file):
    with open(craigs_links_file) as fh:
        contents = fh.readlines()
        craigs_city_links = {}
        for line in contents:
            citytext, craigs_link = line.split("=")
            craigs_link = "".join(craigs_link.split())
            craigs_city_links[citytext] = craigs_link
    return craigs_city_links


def lookup_craigs_url_given_city(citytext, craigs_city_links):
    return craigs_city_links[citytext]


def lookup_city_state_given_zip(zip, zip_code_dict):
    return zip_code_dict[zip]


def generate_documents_to_import_to_mongodb(craigs_city_links, gov_city_state_zips):

    city_state_zip_map = []
    for zip in gov_city_state_zips.keys():
        city, state = lookup_city_state_given_zip(zip, gov_city_state_zips)
        citytext = city + "," + state
        try:
            url = lookup_craigs_url_given_city(citytext, craigs_city_links)
        except KeyError:
            url = None

        x = {
            "zip": zip,
            "Details": {"City": city, "State": state},
            "craigs_local_url": url,
        }
        city_state_zip_map.append(x)
    return city_state_zip_map


def load_zips_to_mongodb(closest_list):
    """ write all the key/values to mongodb """
    client = MongoClient()
    db = client.posts
    posts = db.posts
    new_result = posts.insert_many(closest_list)
    print("Multiple posts: {0}".format(new_result.inserted_ids))


if __name__ == "__main__":

    import sys

    try:
        # Round 1
        gov_city_state_zips = create_zips_city_state_dict_from_local_file(zip_code_file)
        craigs_city_links = create_craigs_url_dict_from_local_file(craigs_links_file)
        city_state_zip_map = generate_documents_to_import_to_mongodb(
            craigs_city_links, gov_city_state_zips
        )
        load_zips_to_mongodb(city_state_zip_map)
        # Round 2

    except Exception as e:
        print(e)
