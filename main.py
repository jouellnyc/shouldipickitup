#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py - interface into flask and mongodb

- This script takes in a zip code from Flask/app.py or via cmd line, and then
determines the right Craiglist URL by qurying 'Zips' or 'AltZips' in MongoDB.
It then returns the free items (see below) associated with that MongoDB doc.

- If no data matches or if MongoDB errors, S.F data will be returned

-This script requires the mongodb helper module.

-This file can also be imported as a module and contains the following
functions:

    * main - the main function of the script

TBD: Input validation. Better outcome if MongoDB is down.
""""

import logging

from lib import mongodb

def main(zip):
    """
    Parameters
    ----------
    zip : str
        zip code the user entered - inbound from Flask or from cmd line.

    Returns
    -------
    all_posts
        A [list] of all the local posts in the free sections
    all_links
        A [list] of all the local posts in the free sections
    city
        [str] - the city associated with the zip (for display only)
    state
        [str] - the state associated with the zip (for display only)

    start_lat \
    start_lng /   to be used to calculate distance (disabled for now)

    """

    start_lat = "40.6490763"
    start_lng = "-73.9762069"

    start_lat = "29.5964"
    start_lng = "-82.2178"

    try:
        """ Given a zip, find the Craigslist Url """
        city, state, url, Items, Urls = \
            mongodb.lookup_craigs_url_citystate_and_items_given_zip(zip)
        city, state = city.capitalize(), state.upper()
        all_posts = Items.values()
        all_links = Urls.values()
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
