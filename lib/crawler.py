#!/home/john/anaconda3/bin/python3.7

''' What do I do? I crawl a Craigslist URL Page and load items into MongoDB '''

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
    print('It Worked. Sending to Mongo...')

howmany = 9 # Set to one more than how many items wanted

mongo_filter = { 'craigs_url': craigs_list_url }
mongo_doc    = { "$set" :  { 'Items' : {}}}
#mongo_doc    = { "$set" : { 'Items' : {'item1': 'text1', 'url1' : 'link1' }}}

for num, each_item in enumerate(craigs_local_posts[0:howmany], start=1):
        each_link = each_item.attrs["href"]
        each_text = each_item.text
        item = f"Item{num}"
        url  = f"Url{num}"
        mongo_doc['$set']['Items'][item] =  each_text
        mongo_doc['$set']['Items'][url]   = each_link

        ''' mongo_doc will look like this:
            mongo_doc    = { "$set":  {
                item1 : each_text1, url1: each_link1,
                item2 : each_text2, url2: each_link2,
                item3 : each_text3, url3: each_link3
                }
            }
        '''
print(mongo_filter, mongo_doc)
mongodb.update_one_document(mongo_filter, mongo_doc)
