#!/home/john/anaconda3/bin/python3

import os
import time

file = "/home/john/gitrepos/shouldipickitup/data/craigs_links.txt"

import requestwrap
from bs4 import BeautifulSoup

# with open(file,'r',encoding="utf-8") as fh:
with open(file, "r") as fh:
    contents = fh.readlines()
    for line in contents:
        try:
            city, link = line.split("=")
            link = link.rstrip("\n")
            print(f"=={city} , {link} ==")
            resp = requestwrap.err_web(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            item = soup.find("h2", {"class": "area"}).get_text()
            print(item)
        except Exception as e:
            print(e)
        else:
            print("wait")
            time.sleep(5)
