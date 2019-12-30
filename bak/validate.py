#!/home/john/anaconda3/bin/python3.7

import re
import sys

from pymemcache.client import base

client = base.Client(('localhost', 11211))

for zip in ("%.5d" % x for x in range(99999)):
        #print("===", zip)
        data         = client.get(zip)
        city, state  = data.decode("utf-8").split(',')
        patt  = re.compile('\w+')
        city  = patt.search(city).group()
        state = patt.search(state).group()
        citytext     = f"{city},{state}"
        #print ("CT:", citytext)
        link         = client.get(citytext)
        if link is not None:
            link =  link.decode("utf-8")
            print(f"{zip}:{link}")         
