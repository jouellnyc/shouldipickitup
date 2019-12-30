#!/home/john/anaconda3/bin/python3.7

from pymongo import MongoClient


def lookup_craigs_url_given_zip(zip):
    ''' Given a zip, return a craiglist url '''
    client = MongoClient()
    db = client.posts
    posts = db.posts
    response = posts.find_one({'zip': zip})
    if response is None:
        raise ValueError
    else:
        url = response['craigs_local_url']
        return url


def lookup_city_state_given_zip(zip):
    ''' Given a zip, return city, state '''
    client = MongoClient()
    db = client.posts
    posts = db.posts
    response = posts.find_one({'zip': zip})
    city, state = response['Details']['City'], response['Details']['State']
    return city, state


def load_zips_to_mongodb(closest_list):
    ''' write all the key/values to mongodb '''
    client = MongoClient()
    db = client.posts
    posts = db.posts
    new_result = posts.insert_many(closest_list)
    print('Multiple posts: {0}'.format(new_result.inserted_ids))
