#!/home/john/anaconda3/bin/python3.7

import sys

from pymemcache.client import base


try:
    citytext = sys.argv[1]
except IndexError as e:
    print("tell me some citytext")
    sys.exit(1)

client = base.Client(("localhost", 11211))
print(client.get(sys.argv[1]))
