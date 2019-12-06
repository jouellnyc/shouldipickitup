#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requestwrap
from bs4 import BeautifulSoup
from pymemcache.client import base

def make_craigs_city_url_dict_web():
    ''' make dictionary of cities live from the web '''
    url   = 'https://geo.craigslist.org/iso/us'
    resp  = requestwrap.err_web(url)
    soup  = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')

    craigs_zip_links = {}
    for x in links:
        if not x['href'].startswith(('https://www.c','http://www.c','//','forums',\
            'https://play.goog','https://apps.apple.com')):
            url = x['href']
            url = link.replace(" ", "")
            citytext = x.text
            citytext = citytext.replace(" ", "")
            print(f"{citytext} {url}")
            craigs_zip_links[citytext] = url
    return craigs_zip_links

def write_craigs_city_url_dict_to_file(dict,file):
    fh = open(file,'w')
    for citytext,url in dict.items():
        fh.write(str(citytext) +"=" + str(url) + "\n")
    fh.close()

def load_craigs_city_url_dict_to_memcached(dict):
    client = base.Client(('localhost', 11211))
    for citytext,url in dict.items():
        client.set(citytext,url)

def lookup_craigs_url(citytext):
    client = base.Client(('localhost', 11211))
    link   = client.get(citytext)
    return link

if __name__ == "__main__":
    file  = 'craigs_links.txt'
    all_craigs_cities_and_urls = make_craigs_city_url_dict_web()
    write_craigs_city_url_dict_to_file(all_craigs_cities_and_urls,file)
    load_craigs_city_url_dict_to_memcached(all_craigs_cities_and_urls)
