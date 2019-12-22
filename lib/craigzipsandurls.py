#!/home/john/anaconda3/bin/python3.7


''' Build and load urls for craigslist and a zip code map. Load         '''
''' it into memcached and make available functions to return that data  '''

from bs4 import BeautifulSoup
from pymemcache.client import base

craigs_links_file = '/home/john/gitrepos/shouldipickitup/data/craigs_links.txt'

def make_craigs_city_url_dict_web():
    ''' make dictionary of cities live from the web '''
    url   = 'https://geo.craigslist.org/iso/us'
    resp  = requestwrap.err_web(url)
    soup  = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')

    craigs_zip_links = {}
    for x in links:
        if not x['href'].startswith(('https://www.c','http://www.c','//',
           'https://forums','https://play.goog','https://apps.apple.com')):
            url = x['href']
            url = url.replace(" ", "")
            citytext = x.text
            citytext = citytext.replace(" ", "")
            #print(f"{citytext} {url}")
            craigs_zip_links[citytext] = url
    return craigs_zip_links

def write_craigs_city_url_dict_to_file(dict,file):
    fh = open(file,'w')
    for citytext,url in dict.items():
        fh.write(str(citytext) +"=" + str(url) + "\n")
    fh.close()

def create_craigs_url_dict_from_disk():
    with open(craigs_links_file) as fh:
        contents = fh.readlines()
        web_links = {}
        for line in contents:
            citytext , craigs_link = line.split("=")
            #remove spaces/newlines
            craigs_link = ''.join(craigs_link.split())
            web_links[citytext] = craigs_link
    return web_links

def lookup_craigs_url_from_dict_file(*args):
    #craigs_links_file = '/home/john/gitrepos/shouldipickitup/data/craigs_links.txt'
    #web_links = create_craigs_url_dict_from_disk(craigs_links_file)
    try:
        citytext  = args[0]
        web_links = args[1]
    except IndexError:
        #web_links = web_links
        pass #???
    print(web_links[citytext])
    return web_links[citytext]


def write_craigs_city_url_dict_to_memcached(dict):
    client = base.Client(('localhost', 11211))
    for citytext,url in dict.items():
        client.set(citytext,url)

def lookup_craigs_url_memcached(citytext):
    client = base.Client(('localhost', 11211))
    link   = client.get(citytext)
    if link is None:
         raise ValueError('No data')
    else:
        return link

if __name__ == "__main__":

    import sys
    import requestwrap

    try:
         citytext = sys.argv[1]
    except IndexError as e:
        print(e,"Did you specify city text?")
        sys.exit()

    #craigs_links_file = '/home/john/gitrepos/shouldipickitup/data/craigs_links.txt'
    #all_craigs_cities_and_urls = make_craigs_city_url_dict_web()
    #write_craigs_city_url_dict_to_file(all_craigs_cities_and_urls,craigs_links_file)
    #load_craigs_city_url_dict_to_memcached(all_craigs_cities_and_urls)
    #web_links = create_craigs_url_dict_from_disk(craigs_links_file)
    web_links = create_craigs_url_dict_from_disk()
    lookup_craigs_url_from_dict_file(citytext,web_links)

else:
    from . import requestwrap
