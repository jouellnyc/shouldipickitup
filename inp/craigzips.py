#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requestwrap
from bs4 import BeautifulSoup
from pymemcache.client import base

def make_craigs_city_dict_web():
    ''' make dictionary of cities live from the web '''
    url   = 'https://geo.craigslist.org/iso/us'
    resp  = requestwrap.err_web(url)
    soup  = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')
    
    craigs_zip_links = {}
    for x in links: 
        if not x['href'].startswith(('https://www.c','http://www.c','//','forums',\
            'https://play.goog','https://apps.apple.com')):
            print(f"{x['href']} {x.text}") 
            craigs_zip_links[x.text] = x['href']
    return craigs_zip_links

def write_links_to_file(dict):
    file  = 'craigs_links.txt'
    fh = open(file,'w')
    for key,value in dict.items():
        fh.write(str(key) +"=" + str(value) + "\n")
    fh.close()

def load_links_to_memcached(dict):
    client = base.Client(('localhost', 11211))
    for key,value in dict.items():
        client.set(key,value)

def lookup_craigs_url(city):
    client = base.Client(('localhost', 11211))
    link   = client.get(city)
    return link 

if __name__ == "__main__":
    all_craigs_links = make_craigs_city_dict_web()
    #write_links_to_file(all_craigs_links)
    load_links_to_memcached(all_craigs_links)
