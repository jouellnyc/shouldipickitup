#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib import mongodb
from lib import websitepuller

def main(zip):

    start_lat = '40.6490763'
    start_lng = '-73.9762069'

    start_lat = '29.5964'
    start_lng = '-82.2178'


    ''' Given a zip, find the Craigslist Url '''
    try:
        craigs_list_url = mongodb.lookup_craigs_url_given_zip(zip)
        city, state     = mongodb.lookup_city_state_given_zip(zip)
        print(craigs_list_url, city, state )
    except ValueError as e:
        print(craigs_list_url)
    except ConnectionRefusedError:
        pass
    except Exception as e:
        print(e)

    ''' Given the the closest local Craigslist url, return the free items '''
    print('h2')
    craigs_local_url   = craigs_list_url + "/d/free-stuff/search/zip"
    print('h3')
    craigs_local_posts = websitepuller.lookup_craigs_posts(craigs_local_url)

    ''' Given the free items, see:                      '''
    ''' 1) How far away?                                '''
    ''' 2) How much on Ebay                             '''
    ''' 3) How much for a Lyft                          '''

    ''' only show me a few items '''

    all_posts = []
    all_links = []

    for each_item in craigs_local_posts[0:3]:

        each_link = (each_item.attrs['href'])
        end_lat,end_lng,miles  = websitepuller.lookup_miles_from_user(each_item,start_lat,start_lng)
        #price                  = websitepuller.lookup_price_on_ebay(each_item)
        price = 5
        #mind,maxd              = websitepuller.lookup_cost_lyft(start_lat,start_lng,end_lat,end_lng)
        mind,maxd = 8, 9
        printable_data         = (f"{each_item.text} is selling for {price} on "
            f"Ebay and is {miles:.2f} miles away from you. Using Lyft it will "
            f"cost between {mind} and {maxd} dollars to pick up.\n")
        all_posts.append(printable_data)
        all_links.append(each_link)
    all_links = enumerate(all_links,1)
    return all_posts, all_links, city.capitalize(), state.upper()

if __name__ == "__main__":

    import sys

    try:
        zip = sys.argv[1]
    except IndexError as e:
        print(e,"Did you specify a zip?")
        sys.exit()

    try:
        print (main(zip))
    except Exception as e:
        print(e)
