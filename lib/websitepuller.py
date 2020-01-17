#!/usr/bin/env python3

""" websitepuller.py - pull data for *each* item  - Ebay, Lyft or Craiglist

- This script takes in a zip code from Flask/app.py or via cmd line, and then
determines the right Craiglist URL by qurying 'Zips' or 'AltZips' in MongoDB.
It then returns the free items (see below) associated with that MongoDB doc.

-This script requires the requests BeautifulSoup module and geopy

-This file is meant to be imported as a module.

-This file contains the following functions:

"""


import re
import sys
import json

from bs4 import BeautifulSoup
from geopy.distance import geodesic

try:
    from lib import requestwrap  # if called from ..main()
except ModuleNotFoundError:
    import requestwrap  # if called from .


def lookup_craigs_posts(craigs_list_url):
    """
    Parameters
    ----------
    craigs_list_url : str
        The 'local' Craig list url.

    Returns
    -------
    craigs_posts : list
        A list of all the BeautifulSoup objects containing free items
    """
    craigs_response = requestwrap.err_web(craigs_list_url)
    craigs_soup = BeautifulSoup(craigs_response.text, "html.parser")
    craigs_posts = craigs_soup.find_all("a", class_="result-title hdrlnk")
    return craigs_posts


mapsre = re.compile("https://www.google.com/maps/preview/")


def lookup_miles_from_user(each_item, start_lat, start_lng):
    """
    Parameters
    ----------
    each_item : BeautifulSoup object
        Pointer to each free item

    Returns
    -------
    end_lat - string
        Final latitude - where the free item is
    end_lng
        Final longitude - - where the free item is
    miles - int
        Distance from user

    Exceptions
        AttributeError - a post without any text
    """
    item_url = each_item.attrs["href"]
    craigs_resp = requestwrap.err_web(item_url)
    craigs_soup = BeautifulSoup(craigs_resp.text, "html.parser")
    googurl = craigs_soup.find("a", href=mapsre)

    try:
        end_lat, end_lng, _ = (
            googurl.attrs["href"].split("@")[1].split("z")[0].split(",")
        )
        miles = geodesic((start_lat, start_lng), (end_lat, end_lng)).mi
        return end_lat, end_lng, miles
    except AttributeError:
        print(f"{each_item.text} was likely deleted")
        raise


def lookup_price_on_ebay(each_item):
    """
    Parameters
    ----------
    each_item : BeautifulSoup object - bs4.element.Tag
        Pointer to each free item

    Returns
    -------
    price - string
        Price as per Ebay
    Exceptions
        AttributeError - a post without any price info
    """

    ebay_url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="
    ebay_path = (
        f"{each_item.text}&_sacat=0&LH_TitleDesc=0&_osacat=0&_odkw={each_item.text}"
    )
    ebay_query_url = ebay_url + ebay_path
    ebay_resp = requestwrap.err_web(ebay_query_url)
    ebay_soup = BeautifulSoup(ebay_resp.text, "html.parser")

    try:
        item = ebay_soup.find("h3", {"class": "s-item__title"}).get_text(separator=" ")
        print(item)
    except AttributeError:
        raise ValueError("no match")
    else:
        try:
            price = ebay_soup.find("span", {"class": "s-item__price"}).get_text()
        except AttributeError:
            raise ValueError("no price")
        else:
            return price


def lookup_cost_lyft(start_lat, start_lng, end_lat, end_lng):
    """
    Parameters
    ----------
    start_lat, start_lng, end_lat, end_lng - strings
        - Start latitude and longitude from user to item

    Returns
    -------
    mind, maxd - strings
        - minimum and maximum Lyft cost
    """
    lyft_url = "http://www.lyft.com"
    lyft_path = f"/api/costs?start_lat={start_lat}&start_lng={start_lng}&end_lat={end_lat}&end_lng={end_lng}"
    lyft_costurl = lyft_url + lyft_path
    lyft_resp = requestwrap.err_web(lyft_costurl)
    fares = json.loads(lyft_resp.content)
    min = fares["cost_estimates"][0]["estimated_cost_cents_min"]
    max = fares["cost_estimates"][0]["estimated_cost_cents_max"]
    mind = min / 100
    maxd = max / 100
    return mind, maxd
