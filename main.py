#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from lib import mongodb
from lib import websitepuller

def main(zip):

    start_lat = "40.6490763"
    start_lng = "-73.9762069"

    start_lat = "29.5964"
    start_lng = "-82.2178"

    """ Given a zip, find the Craigslist Url """
    try:

        city, state, craigs_list_url, items = mongodb.lookup_craigs_url_citystate_and_items_given_zip(zip)
        city, state = city.capitalize(), state.upper()
        all_posts = items[0:4]
        all_links = items[4:8]
        all_links = enumerate(all_links, start = 1)
        return all_posts, all_links, city, state

    except (ValueError, ConnectionRefusedError, ServerSelectionTimeoutError, KeyError) as e:

        logging.exception('Caught an error')
        craigs_list_url = "https://sfbay.craigslist.org"
        city, state = (
            (f"Sorry didn't find data for {zip}, here's items for " f"San Francisco "),
            "CA",
        )
        print(city, state)

    except Exception as e:
        print("Error", e)
    else:
        print("Debug:", craigs_list_url, city, state, items)

        """ Given the free items, see:                      """
        """ 1) How far away?                                """
        """ 2) How much on Ebay                             """
        """ 3) How much for a Lyft                          """



if __name__ == "__main__":

    import sys

    try:
        zip = sys.argv[1]
    except IndexError as e:
        print(e, "Did you specify a zip?")
        sys.exit()

    try:
        print(main(zip))
    except Exception as e:
        print(e)
