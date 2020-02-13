#!/usr/bin/env python3

""" crawler.py  - Web Crawler

-This script:
    - Takes in a Craigslist URL
    - Crawls the page
    - Prepares a MongoDB insert_one_document
    - Sends data to  MongoDB

-If no data matches or if MongoDB errors, S.F data will be returned
-This script requires the mongodb and websitepuller helper modules.
-This file is mean to be run outside of the Flask Appself.

"""

import os
import sys
import time
import logging
from random import randrange

import mongodb
import websitepuller
import pickledata
from pymongo.errors import ConnectionFailure


#"crawler.log"
logname = os.path.splitext(os.path.basename(__file__))[0] + ".log"

logging.basicConfig(
    filename=logname,
    level="INFO",
    format="%(levelname)s %(asctime)s %(module)s %(process)d  %(message)s"
)

def get_web_data(craigs_list_url):
    """ Return SF data from local if Mongdb is down/server Timeout.
    Parameters
    ----------
    craigs_list_url
        str - local Craigs List Url

    Returns
    -------
    craigs_local_posts
        beautiful soup_object - list of all free items
    """
    craigs_local_url = craigs_list_url + "/d/free-stuff/search/zip"
    craigs_local_posts = websitepuller.lookup_craigs_posts(craigs_local_url)
    return craigs_local_posts


def get_ebay_data(craigs_local_posts, random="yes", howmany=12):

    if random == "yes":
        sleep = randrange(15, 45)
    else:
        sleep = 0
    ebay_prices = []
    ebay_links = []
    for each in craigs_local_posts[0:howmany]:
        try:
            price, eb_link = websitepuller.lookup_price_on_ebay(each)
        except ValueError:
            price = "No intere$t on Ebay$"
            link = "No $$ data on Ebay$"
        else:
            price = price.replace("$", "")
            try:
                float(price)
            except ValueError:
                price = "No $ data on Ebay$"
            else:
                price = price
        finally:
            ebay_prices.append(price)
            ebay_links.append(eb_link)
        time.sleep(sleep)
    return ebay_prices, ebay_links


def format_mongodocs(soup_object, ebay_prices, ebay_links, howmany=12):
    """ Return Formatted Mongdo Doc
    Parameters
    ----------
    soup_object
        beautiful soup_object - list of all free items crawled
    howmany
        number of items to return from CL page

    Returns
    -------
    mongo_doc
        dictionary of dictionaries  - mongo_doc object -

    - We use an Embedded Mongo Doc to List Items and URls

     mongo_doc will look like this:
                {
                    "$set":

                    { Items:

                    item1 : each_text1, url1: each_link1,
                    item2 : each_text2, url2: each_link2,
                    item3 : each_text3, url3: each_link3

                    }
                }
    """
    mongo_filter = {"craigs_url": craigs_list_url}
    mongo_doc = {"$set": {"Items": {}, "Urls": {}, "Prices": {}, "EbayLinks": {}}}

    for num, each_item in enumerate(soup_object[0:howmany], start=1):
        each_link = each_item.attrs["href"]
        each_text = each_item.text
        item = f"Item{num}"
        url = f"Url{num}"
        mongo_doc["$set"]["Items"][item] = each_text
        mongo_doc["$set"]["Urls"][url] = each_link

    for num, price in enumerate(ebay_prices[0:howmany], start=1):
        price_num = f"Price{num}"
        mongo_doc["$set"]["Prices"][price_num] = price

    for num, link in enumerate(ebay_links[0:howmany], start=1):
        link_num = f"EbayLink{num}"
        mongo_doc["$set"]["EbayLinks"][link_num] = link

    return mongo_doc


if __name__ == "__main__":


    try:

        verbose = True 
        howmany = 12
        craigs_list_url = sys.argv[1]
        noindex = sys.argv[2]
        craig_posts = get_web_data(craigs_list_url)
        ebay_prices, ebay_links = get_ebay_data(
            craig_posts, random = "no", howmany = howmany
        )
        mongo_doc = format_mongodocs(craig_posts, ebay_prices, ebay_links, howmany = howmany )
        mongo_filter = {"craigs_url": craigs_list_url}
        if verbose:
            print(mongo_doc)

    except IndexError as e:
        print("URL or Indexing?")
        sys.exit()

    except (ValueError, NameError) as e:
        logging.exception(e)

    else:
        if noindex == "noindex":
            print("Pickling...")
            pickledata.save(mongo_doc)
        else:
            print("Sending to Mongo")
            try:
                mongodb.update_one_document(mongo_filter, mongo_doc)
            except ConnectionFailure as e:
                logging.error(e)
                if verbose:
                    print(e)
            except Exception as e:
                msg = "Uncaught Error"
                if verbose:
                    print(f"{msg}: Check crawl log")
                logging.exception(f"{msg}: {e}")
            else:
                print("Sent to Mongo Success")
