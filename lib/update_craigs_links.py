#!/usr/bin/env python3

import time
import crawler

file1  = "../non-app/all_urls.txt"
file2  = "../data/craigs_links2.txt"

map = []
with open(file1,'r') as fh:
    for url in fh:
        url=url.rstrip()
        print("===",url)
        try:
            c,s = crawler.get_city_from_first_free_cl_item(url)
        except TypeError as e:
            print("no data for", url)
        else:
            print(c,s)
            time.sleep(10)
            print(url,c,s)
            map.append( (url,c,s) )

with open(file2,'w') as fh:
    for each in map:
        url, c , s = each
        fh.write(f"{c},{s}={url}\n")
