#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Created on Wed Nov 20 17:01:23 2019

@author: jouell

"""

import re
import json
import requestwrap
from bs4 import BeautifulSoup
from geopy.distance import geodesic

myzip = '11218'
start_lat  = '40.6490763'
star_long  = '-73.9762069'

craigs_main_url   = f'https://newyork.craigslist.org/search/brk/zip?postal={myzip}'
craigs_main_resp  = requestwrap.err_web(craigs_main_url)
craigs_main_soup  = BeautifulSoup(craigs_main_resp.text, 'html.parser')
craigs_main_posts = craigs_main_soup.find_all('a', class_= 'result-title hdrlnk')
mapsre            = re.compile("https://www.google.com/maps/preview/")

lyft_url     = "http://www.lyft.com"
ebay_url     = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="

for each_item in craigs_main_posts:

    item_url          = each_item.attrs['href']
    craigs_resp       = requestwrap.err_web(item_url)
    craigs_soup       = BeautifulSoup(craigs_resp.text, 'html.parser')
    googurl           = craigs_soup.find('a', href=mapsre)
    try:
        lat,lon, _        = googurl.attrs['href'].split('@')[1].split('z')[0].split(',')
    except AttributeError:
        print(f"{each_item.text} was likely deleted")
        pass
    miles             = geodesic((start,end),(lat,lon)).miles

    ebay_path      = f"{each_item.text}&_sacat=0&LH_TitleDesc=0&_osacat=0&_odkw={each_item.text}"
    ebay_query_url = ebay_url + ebay_path
    ebay_resp      = requestwrap.err_web(ebay_query_url)
    ebay_soup      = BeautifulSoup(ebay_resp.text, 'html.parser')
    item           = ebay_soup.find("h3", {"class": "s-item__title"}).get_text(separator=u" ")
    price          = ebay_soup.find("span", {"class": "s-item__price"}).get_text()


    lyft_path = f"/api/costs?start_lat={start_log}&start_lng={start_long}
                 "&end_lat={end_lat}&end_lng={end_lon}"
    lyft_costurl = lyft_url + lyft_path
    lyft_resp = requestwrap.err_web(lyft_costurl)
    lyft_resp.content
    fares = json.loads(lyft_resp.content)
    min   = fares['cost_estimates'][0]['estimated_cost_cents_min']
    max   = fares['cost_estimates'][0]['estimated_cost_cents_max']
    mind  = min/100
    maxd  = max/100

    print (f"\"{each_item.text}\" is Free on Craigslist, is selling for {price}"
           f" on Ebay and is {miles:.2f} miles away from you. Using Lyft it will "
           f"cost between {mind} and {maxd} dollars to pick up.")
    print("\n")
