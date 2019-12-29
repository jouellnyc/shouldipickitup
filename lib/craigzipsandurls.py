#!/home/john/anaconda3/bin/python3.7

''' Build and load urls for craigslist and a zip code map. Load            '''
''' it into memcached and make available functions to return that data     '''

''' Specifically this module only cares about citytext to craigslist link: '''
'''        'dallas/fortworth' => 'https://dallas.craigslist.org            '''
'''        'all  lower  case'                                              '''
''' We support 169 out the 450+ craigslist links (see.. data/cities.txt)   '''
''' It will take a bit more effort to de-obfuscate the others              '''

from bs4 import BeautifulSoup
from pymemcache.client import base

craigs_links_file = '/home/john/gitrepos/shouldipickitup/data/craigs_links.txt'

def make_craigs_city_url_dict_web():
    ''' make dictionary of cities live from the web               '''

    url   = 'https://geo.craigslist.org/iso/us'
    resp  = requestwrap.err_web(url)
    soup  = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')

    citytext_to_craiglinks = {}
    for x in links:
        if not x['href'].startswith(('https://www.c','http://www.c','//',
           'https://forums','https://play.goog','https://apps.apple.com')):
            url = x['href']
            url = url.replace(" ", "")
            citytext = x.text
            citytext = citytext.replace(" ", "")
            #print(f"{citytext} {url}")
            citytext_to_craiglinks[citytext] = url
    return citytext_to_craiglinks

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
        print(link.decode('UTF-8'))
        return link

def lookup_items_in_zip_memcached(zip):
    zip_item_key = zip + '-'
    client = base.Client(('localhost', 11211))
    resp = client.get(zip_item_key).decode("utf-8")
    items = resp.split(":")
    return items


if __name__ == "__main__":

    import sys
    import requestwrap

    try:

        citytext = sys.argv[1]
        if len(sys.argv) > 2:
            citytext = sys.argv[1]
            where    = sys.argv[2]
            if where == 'file':
                web_links = create_craigs_url_dict_from_disk()
                lookup_craigs_url_from_dict_file(citytext,web_links)
            elif where == 'memcached':
                lookup_craigs_url_memcached(citytext)
            else:
                print("from where?")
                sys.exit(1)
        else:
            if sys.argv[1] == 'load_mem':
                web_links = create_craigs_url_dict_from_disk()
                write_craigs_city_url_dict_to_memcached(web_links)
            elif sys.argv[1] == 'web_get':
                all_craigs_cities_and_urls = make_craigs_city_url_dict_web()
                write_craigs_city_url_dict_to_file(all_craigs_cities_and_urls,craigs_links_file)
            else:
                print("try again")
                sys.exit(1)

    except IndexError as e:
            print("Did you specify city text? or load_mem? or web_get?")
            print(len(sys.argv))
            sys.exit()



else:
    import requestwrap
