#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

main.py - interface into flask and mongodb.
- This script takes in a zipcode code from Flask/app.py or via cmd line, and then
determines the right Craiglist URL by qurying 'Zips' or 'AltZips' in MongoDB.
It then returns the free items (see below) associated with that MongoDB doc.

- If there is no data for the zipcode entered, S.F data will be returned
- If MongoDB is down S.F data will be returned (if data was crawled and loaded)

-This script requires the mongodb helper module.

-This file can also be imported as a module and contains the following
functions:

    * main - the main function of the script

TBD: If MondoDB is down don't load a file every time ...

"""

import logging

import pymongo
from pymongo.errors import ConnectionFailure

from lib import mongodb
from lib import pickledata


def main(zipcode):
    """Send data to flask template for display after querying MongoDB.

    Parameters
    ----------
    zipcode : str
        zipcode code the user entered - inbound from Flask or from cmd line.

    Returns
    -------
    all_posts
        A [list] of all the local posts in the free sections
    all_links
        A [list] of all the local posts in the free sections
    city
        [str] - the city associated with the zipcode (for display only)
    state
        [str] - the state associated with the zipcode (for display only)

    start_lat
    start_lng    to be used to calculate distance (disabled for now)

    """
    start_lat = "40.6490763"
    start_lng = "-73.9762069"

    start_lat = "29.5964"
    start_lng = "-82.2178"

    """ Defaults - Worst Case scenario """
    fall_back_url = "https://sfbay.craigslist.org/d/free-stuff/search/zipcode"
    all_posts = ['Items Error'] * 3
    all_links = [fall_back_url] * 3
    all_cust  = list(zip(all_links, all_posts))
    city, state = (f"Sorry didn't find data for {zipcode} "
                   f"here's items for San Francisco", "CA")
    try:

        """ Given a zipcode, find the Craigslist Url """
        city, state, url, Items, Urls, Prices, EBlinks = \
            mongodb.lookup_craigs_url_citystate_and_items_given_zip(zipcode)
        city, state = city.capitalize(), state.upper()
        all_posts   = list(Items.values())
        all_links   = list(Urls.values())
        all_prices  = list(Prices.values())
        all_eblnks  = list(EBlinks.values())
        all_cust    = list(zip(all_eblnks, all_prices))

    except (ValueError, KeyError) as e:

        msg = f"Going to pickle data"
        logging.exception(f"LEmsg=> {msg}, LEtext=>{e}, Type=> {e.__class__.__name__}")
        all_posts, all_links = fallback_to_pickle()

    except ConnectionFailure as e:

        msg = "MondoDB Connection Errors - DB down?"
        logging.error(msg)
        all_posts, all_links = fallback_to_pickle()

    except Exception as e:

        msg = "Unexpected Error=> "
        logging.exception(f"{msg}Text:{e} Type:{e.__class__.__name__}")

    else:

        print("Match:", craigs_list_url, city, state, items)

    finally:
        return all_posts, all_links, all_cust, city, state

        """ Given the free items, see:                      """
        """ 1) How far away?                                """
        """ 2) How much on Ebay                             """
        """ 3) How much for a Lyft                          """

def fallback_to_pickle():
    """ Return SF data from local if Mongdb is down/server Timeout.
    Parameters
    ----------
    none

    Returns
    -------
    all_posts
        A [list] of all the local posts in the free sections
    all_links
        A [list] of all the local posts in the free sections
    """
    try:
        pickled   = pickledata.loadit(file="data/sf.pickle")
        all_posts = list(pickled['$set']['Items'].values())
        all_links = list(pickled['$set']['Urls'].values())
        #all_links = enumerate(all_links, start = 1)
        return all_posts, all_links
    except (IOError, KeyError, TypeError) as e:
        Pmsg = "Even the file is erroring!: "
        Pmsg += str(e)
        logging.error(Pmsg)
        #Sms/page out


if __name__ == "__main__":

    import sys

    try:
        zipcode = sys.argv[1]
    except IndexError as e:
        print(e, "Did you specify a zipcode?")
        sys.exit()

    print("Main: ", main(zipcode))
