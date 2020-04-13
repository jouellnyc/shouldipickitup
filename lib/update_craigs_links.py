#!/usr/bin/python3

#Download all craigslist links and 
#Assign cities by screen scraping or using
#What Craigslist tell us 

import sys
import time
import crawler
import requestwrap
from bs4 import BeautifulSoup

all_urls     = "../non-app/all_urls.txt"
craigs_links = "../data/craigs_links.txt"
new_york     = "../data/new_york.txt"

geo_craigs_url  = "https://geo.craigslist.org/iso/us/"
geo_craigs_req  = requestwrap.err_web(geo_craigs_url)
geo_craigs_soup = BeautifulSoup(geo_craigs_req.text, "html.parser")
with open(all_urls,'w') as fh:
    for link in geo_craigs_soup.find_all('a'):
        url  = link.get('href')
        city = link.string
        city = ''.join(city.split())
        if 'www' not in url  and  'apple.com' not in url and 'google' not  in url and 'forums' not in url:
            fh.write(f"{city}={url}\n")

with open(all_urls,'r') as fh:
    with open(craigs_links,'w', buffering=1) as fh2:
        for line in fh:
            citystate, url = line.split('=')
            if ',' not in line:
                if 'newyorkcity' in citystate:
                    continue
                url = url.rstrip()
                try:
                    c,s = crawler.get_city_from_first_free_cl_item(url)
                except TypeError as e:
                    print("no data for", url)
                else:
                    fh2.write(f"{c},{s}={url}\n")
            else:
                fh2.write(f"{citystate}={url}")
        with open(new_york,'r') as fh3:
            for line in fh:
                fh2.write(line)

