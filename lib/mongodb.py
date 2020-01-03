#!/home/john/anaconda3/bin/python3.7

from pymongo import MongoClient

database_name = "shoulidpickitup"
collection_name = "data"

#def ConnectToMongo(database_name=database_name, collection_name=collection_name):
def ConnectToMongo(database_name="shoulidpickitup", collection_name="data"):
    client = MongoClient()
    database_handle = client[database_name]
    collection_handle = database_handle[collection_name]
    return collection_handle


def lookup_craigs_url_given_zip(zip):
    """ Given a zip, return a craiglist url """
    dbh = ConnectToMongo()
    response = dbh.find_one({"zip": zip})
    if response is None:
        raise ValueError("No data in Mongo for " + str(zip))
    else:
        url = response["craigs_url"]
        return url


def lookup_city_state_given_zip(zip):
    """ Given a zip, return city, state """
    dbh = ConnectToMongo()
    response = dbh.find_one({"zip": zip})
    if response is None:
        raise ValueError("No data in Mongo for " + str(zip))
    else:
        city, state = response["City"], response["State"]
        return city, state

def lookup_craigs_posts(zip):
    dbh = ConnectToMongo()
    response = dbh.find_one({"zip": zip})
    if response is None:
        raise ValueError
    else:
        return ([response['Item1'], response['Item2'], response['Item3'] , response['Item4']],
                [response['Url1'] , response['Url2'] , response['Url3']  ,  response['Url4']])


def update_one_document(mongo_filter, mongo_doc):
    """ update one doc to mongodb """
    dbh = ConnectToMongo()
    new_result = dbh.update_one(mongo_filter, mongo_doc)
    print(new_result.raw_result)


def init_load_city_state_zip_map(closest_list):
    """ write all the key/values to mongodb """
    dbh = ConnectToMongo()
    new_result = dbh.insert_many(closest_list)
    print("Multiple posts: {0}".format(new_result.inserted_ids))
