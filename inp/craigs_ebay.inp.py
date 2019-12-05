#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Created on Wed Nov 20 17:01:23 2019

@author: jouell 

"""

import re
import sys
#import json
import requestwrap
from bs4 import BeautifulSoup
from geopy.distance import geodesic                                                                                  

import zip2dict
import czips
zipcode = sys.argv[1]


#Create zip db
myzips  = zip2dict.csv_handler()

#Given a zip, find the closest numerial match and return city, state name
closest_city, closest_state = zip2dict.lookup_craigs_urls(zipcode,myzips)
print(closest_city, closest_state)

#Given a city name, find the closest Craigslist Url
craigs_links = czips.make_craigs_city_dict()
closest_craigs_list_url = czips.lookup_craigs_url(closest_city,craigs_links)
print(closest_craigs_list_url)

sys.exit()                            

start  = '40.6490763'
end    = '-73.9762069'                                                                                     

myzip = '32613'

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
   
  
   
    print (f"\"{each_item.text}\" is Free on Craigslist, is selling for {price}" 
           f" on Ebay and is {miles:.2f} miles away from you.")                                         
