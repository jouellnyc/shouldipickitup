#!/home/john/anaconda3/bin/python3.7

from pymongo import MongoClient

def ConnectToMongo():
    client = MongoClient()
    db = client.posts
    posts = db.posts
    return posts

def lookup_craigs_url_given_zip(zip):
    ''' Given a zip, return a craiglist url '''
    client = ConnectToMongo()
    response = client.find_one({'zip': zip})
    if response is None:
        raise ValueError
    else:
        url = response['craigs_url']
        return url

def lookup_city_state_given_zip(zip):
    ''' Given a zip, return city, state '''
    client = ConnectToMongo()
    response = client.find_one({'zip': zip})
    city, state = response['City'], response['State']
    return city, state

def load_zips_to_mongodb(closest_list):
    ''' write all the key/values to mongodb '''
    client = ConnectToMongo()
    new_result = client.insert_many(closest_list)
    print('Multiple posts: {0}'.format(new_result.inserted_ids))

def update_one_document_in_mongodb(mongo_filter, mongo_doc):
    ''' write all the key/values to mongodb '''
    client = ConnectToMongo()
    new_result = client.update_one(mongo_filter, mongo_doc)
    print(new_result.raw_result)
