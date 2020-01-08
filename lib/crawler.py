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

import sys

import mongodb
import websitepuller

craigs_list_url = sys.argv[1]

try:
    craigs_local_url = craigs_list_url + "/d/free-stuff/search/zip"
    craigs_local_posts = websitepuller.lookup_craigs_posts(craigs_local_url)
except (ValueError, NameError) as e:
    print("Error: ", e)
    sys.exit()
else:
    print("It Worked. Sending to Mongo...")

howmany = 9  # Set to one more than how many items wanted
mongo_filter = {"craigs_url": craigs_list_url}
mongo_doc = {"$set": {"Items": {}, "Urls": {}}}

""" We use an Embedded Mongo Doc  to List Items and URls """
""" Python wise that means a dictionary of dictionaries  """

for num, each_item in enumerate(craigs_local_posts[0:howmany], start=1):
    each_link = each_item.attrs["href"]
    each_text = each_item.text
    item = f"Item{num}"
    url = f"Url{num}"
    mongo_doc["$set"]["Items"][item] = each_text
    mongo_doc["$set"]["Urls"][url] = each_link

    """ mongo_doc will look like this:
            {
                "$set":

                { Items:

                item1 : each_text1, url1: each_link1,
                item2 : each_text2, url2: each_link2,
                item3 : each_text3, url3: each_link3

                }
            }
        """
print(mongo_filter, mongo_doc)
mongodb.update_one_document(mongo_filter, mongo_doc)
