#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:

    import re
    import sys

    # import json
    from lib import requestwrap
    from bs4 import BeautifulSoup
    from geopy.distance import geodesic
    import govzipsandcities
    import craigzipsandurls

except Exception as e:
    print("Error:", e)

zipcode = sys.argv[1]

# Given a zip, find the closest numerial match and return city,state names
city, state = govzipsandcities.lookup_city_state_given_zip(zipcode)
# print(city,state)

# Given a city name, find the closest Craigslist Url
citytext = f"{city},{state}"
# print(citytext)
craigs_list_url = craigzipsandurls.lookup_craigs_url(citytext).decode("UTF-8")
print(f"{citytext} is available at {craigs_list_url}")

sys.exit()


start = "40.6490763"
end = "-73.9762069"

myzip = "32613"

craigs_main_url = f"https://newyork.craigslist.org/search/brk/zip?postal={myzip}"
craigs_main_resp = requestwrap.err_web(craigs_main_url)
craigs_main_soup = BeautifulSoup(craigs_main_resp.text, "html.parser")
craigs_main_posts = craigs_main_soup.find_all("a", class_="result-title hdrlnk")
mapsre = re.compile("https://www.google.com/maps/preview/")

lyft_url = "http://www.lyft.com"
ebay_url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="


for each_item in craigs_main_posts:

    item_url = each_item.attrs["href"]
    craigs_resp = requestwrap.err_web(item_url)
    craigs_soup = BeautifulSoup(craigs_resp.text, "html.parser")
    googurl = craigs_soup.find("a", href=mapsre)
    try:
        lat, lon, _ = googurl.attrs["href"].split("@")[1].split("z")[0].split(",")
    except AttributeError:
        print(f"{each_item.text} was likely deleted")
        pass
    miles = geodesic((start, end), (lat, lon)).miles

    ebay_path = (
        f"{each_item.text}&_sacat=0&LH_TitleDesc=0&_osacat=0&_odkw={each_item.text}"
    )
    ebay_query_url = ebay_url + ebay_path
    ebay_resp = requestwrap.err_web(ebay_query_url)
    ebay_soup = BeautifulSoup(ebay_resp.text, "html.parser")
    item = ebay_soup.find("h3", {"class": "s-item__title"}).get_text(separator=" ")
    price = ebay_soup.find("span", {"class": "s-item__price"}).get_text()

    print(
        f'"{each_item.text}" is Free on Craigslist, is selling for {price}'
        f" on Ebay and is {miles:.2f} miles away from you."
    )
