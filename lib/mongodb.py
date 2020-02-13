#!/usr/bin/env python3

""" mongodb.py - interface into MongoDB

- This script takes in a zip code uses pymongo to connect to  MongoDB.

- This script requires the pymongo module.

- This file:

    - is intended as a loadable module only.
    - contains the following functions:

     ConnectToMongo
        Connect to MongoDB and return DB handle
     lookup_craigs_url_citystate_and_items_given_zip
        Return all the goodies: items, urls , city , state from MongoDB
     lookup_city_state_given_zip
        Given a zip, return city, state from MongoDB
     lookup_craigs_posts
        Only return the free items text
     update_one_document
        Update one doc to mongodb regardless if exists
     insert_one_document
        Insert one doc to mongodb
     init_load_city_state_zip_map
        Write all the key/values to mongodb

TBD: Reuse the MongoDB handles.
"""

from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

import logging

database_name = "shouldipickitup"
collection_name = "data"


class AllData:
    """ The usual suspect here, initialized to bare/default """

    def __init__(self):
        self.citytext = ""
        self.city, self.state = ("", "")
        self.url = ""
        self.Items = {}
        self.Urls = {}
        self.Prices = {}
        self.EBlinks = {}


def ConnectToMongo(database_name="shouldipickitup", collection_name="data"):
    """
    Return a database_handle to the caller

    Parameters
    ----------
    database_name : str
        The Default db name
    collection_name : str
        The Default collection name

    Returns
    -------
        collection_handle :  pymongo connect object
    """
    try:
        client = MongoClient(host="172.18.0.2", serverSelectionTimeoutMS=2000)
        database_handle = client[database_name]
        collection_handle = database_handle[collection_name]
    except ConnectionFailure:
        print("Mongo ConnectionFailure")
        raise GenMongoErr
    else:
        return collection_handle


def lookup_all_data_given_zip(zip):
    """
    Return All free items post, Urls, city and state to the caller

    Parameters
    ----------
    zip : str
        zipcode

    Returns
    -------
    Items
        {dictionary} of all the local posts in the free section
    Url
        [str] - The local craigslist url
    Urls
        {dictionary} of all the urls of the free items
    city
        [str] - the city associated with the zip (for display only)
    state
        [str] - the state associated with the zip (for display only)
    """
    dbh = ConnectToMongo()
    response = dbh.find_one({"$or": [{"Zips": zip}, {"AltZips": zip}]})
    if response is None:
        raise ValueError("No data in Mongo for " + str(zip))
    else:
        try:
            all_data = AllData()
            all_data.citytext = response["CityState"]
            all_data.city, all_data.state = response["CityState"].split(",")
            all_data.url = response["craigs_url"]
            all_data.Items = response["Items"]
            all_data.Urls = response["Urls"]
            all_data.Prices = response["Prices"]
            all_data.EBlinks = response["EbayLinks"]
        except KeyError as e:
            raise ValueError("No details in Mongo for " + str(zip))
        except Exception as e:
            raise
        else:
            return all_data


def lookup_city_state_given_zip(zip):
    """
    Return just the city and state to the caller given a zipcode.

    Parameters
    ----------
    zip : str
        zipcode

    Returns
    ----------
    city
        [str] - the city associated with the zip (for display only)
    state
        [str] - the state associated with the zip (for display only)
    """
    dbh = ConnectToMongo()
    dbh.find_one({"$or": [{"Zips": zip}, {"AltZips": zip}]})
    response = dbh.find_one({"$or": [{"Zips": zip}, {"AltZips": zip}]})
    if response is None:
        raise ValueError("No data in Mongo for " + str(zip))
    else:
        city, state = response["CityState"].split(",")
        return (city, state)


def lookup_craigs_url_given_zip(zip):
    dbh = ConnectToMongo()
    dbh.find_one({"$or": [{"Zips": zip}, {"AltZips": zip}]})
    response = dbh.find_one({"$or": [{"Zips": zip}, {"AltZips": zip}]})
    if response is None:
        raise ValueError("No data in Mongo for " + str(zip))
    else:
        return response["craigs_url"]


def lookup_zips_given_craigs_url(craigs_url):
    dbh = ConnectToMongo()
    response = dbh.find_one({"craigs_url": craigs_url})
    if response is None:
        raise ValueError("No data in Mongo for " + str(craigs_url))
    else:
        return (response["Zips"], response["AltZips"])


def lookup_craigs_posts(zip):
    """
    Return only free items post to the caller

    Parameters
    ----------
    zip : str
        zipcode

    Returns
    -------
    Items
        {dictionary} of all the local posts in the free section
    """
    dbh = ConnectToMongo()
    response = dbh.find_one({"$or": [{"Zips": zip}, {"AltZips": zip}]})
    if response is None:
        raise ValueError
    else:
        return response["Items"]


def update_one_document(mongo_filter, mongo_doc, verbose=False):
    """
    Update only one document in MongoDB, create it if it does not exist.
    Parameters
    ----------
    mongo_filter
        - hash to specify mongo restriction
    mongo_doc
        - key : value pairs making up the document

    Returns
    -------
    Items
        {Mongo object}  of all the local posts in the free section
    """
    dbh = ConnectToMongo()
    new_result = dbh.update_one(mongo_filter, mongo_doc, upsert=True)
    if verbose:
        print(new_result.raw_result)
    return new_result


def insert_one_document(mongo_filter, mongo_doc):
    """
    Insert  only one document in MongoDB; do not create it if it does not exist.

    Parameters
    ----------
    mongo_filter
        - hash to specify mongo restriction
    mongo_doc
        - key : value pairs making up the document

    Returns
    -------
    Items
        {Mongo object}  of all the local posts in the free section
    """
    dbh = ConnectToMongo()
    new_result = dbh.insert_one(mongo_filter, mongo_doc)
    print(new_result.inserted_id)
    return new_result


def init_load_city_state_zip_map(master_mongo_city_state_zip_data, verbose=False):
    """
    Init bulk load of all the data created in MongoDBself.

    Parameters
    ----------
    master_mongo_city_state_zip_data
        - dictionary of dictionaries with all 400+ Mongo documents.

    Returns
    -------
    new_result
        {Mongo object} - success of data loadself.

    Exceptions
    ----------
    Invalid Docs return BulkWriteError
    """
    try:
        dbh = ConnectToMongo()
        new_result = dbh.insert_many(master_mongo_city_state_zip_data)
    except ConnectionFailure as e:
        raise
    except BulkWriteError as bwe:
        print(bwe.details)
        raise
    except Exception as e:
        logging.exception(e)
    else:
        if verbose:
            print("Multiple posts: {0}".format(new_result.inserted_ids))
        return new_result


if __name__ == "__main__":

    import sys

    try:
        argv1 = str(sys.argv[1])
        if len(argv1) == 5:
            print(lookup_city_state_given_zip(zip))
            print(lookup_craigs_url_given_zip(zip))
        else:
            zips, altzips = lookup_zips_given_craigs_url(argv1)
            print("Zips", zips)
            print("AltZips", altzips)
    except ConnectionFailure as e:
        print("ConnectionFailure: ", e)
    except Exception as e:
        logging.exception(e)
