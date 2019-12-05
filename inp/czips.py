#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 23:01:49 2019

@author: john
"""

import requestwrap
from bs4 import BeautifulSoup


def make_craigs_city_dict():
    ''' make dictionary of cities '''
    #Get Craigslist city data
    url   = 'https://geo.craigslist.org/iso/us'
    resp  = requestwrap.err_web(url)
    soup  = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')
    
    craigs_zip_links = {}
    for x in links: 
        if not  x['href'].startswith( ('https://www.c','http://www.c','//','forums') ): 
            #print(f"{x['href']} {x.text}") 
            craigs_zip_links[x.text] = x['href']
    return    craigs_zip_links
     
def lookup_craigs_url(city,dictionary):
    return [ value for key, value in dictionary.items() if city.lower() in key ]


if __name__ == "__main__":
    mylist = make_craigs_city_dict()
    print(mylist)
    myurl = lookup_craigs_url('gainesville',mylist )
    print(myurl)
    print('hie')


