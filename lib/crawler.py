#!/home/john/anaconda3/bin/python3.7

''' What do I do? I crawl a single zip code and load the first 3 items into Mongo '''

import sys

import mongodb
import websitepuller

craigs_list_url = sys.argv[1]
action          = sys.argv[2]

try:
    craigs_local_url = craigs_list_url + "/d/free-stuff/search/zip"
    craigs_local_posts = websitepuller.lookup_craigs_posts(craigs_local_url)
except (ValueError, NameError) as e:
    print("Error: ", e)
    sys.exit()
else:
    print('It Worked. Sending to Mongo...')

mongo_filter = { 'craigs_url': craigs_list_url }
if action == "update":
    mongo_doc = { "$set": {} }
    for num, each_item in enumerate(craigs_local_posts[0:8], start=1):
            each_link = each_item.attrs["href"]
            each_text = each_item.text
            item = f"Item{num}"
            url  = f"Url{num}"
            mongo_doc['$set'][item] = each_text
            mongo_doc['$set'][url]  = each_link
    print(mongo_filter, mongo_doc)
    mongodb.update_one_document(mongo_filter, mongo_doc)
elif action == "insert":
    pass
    mongo_doc = {}
    mongo_doc[item] = each_text
    mongo_doc[url]  = each_link
    mongodb.insert_one_document(mongo_filter, mongo_doc)
    ''' mongo_doc will look like this:
        mongo_doc    = { "$set":  {
            item1 : each_text1, url1: each_link1,
            item2 : each_text2, url2: each_link2,
            item3 : each_text3, url3: each_link3
            }
        }
    '''
