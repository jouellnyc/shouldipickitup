#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

    except (ValueError, ConnectionRefusedError, ServerSelectionTimeoutError) as e:

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


    """ Given the the closest local Craigslist url, return the free items """
    try:

        all_posts, all_links = mongodb.lookup_craigs_posts(zip)

    except (KeyError, ValueError, ConnectionRefusedError, ServerSelectionTimeoutError) as e:
        ''' If there are no items whatsoever, if ItemX DNE '''

        print("NoMo Mongo: ", e) #Why print Item1?
        all_posts = []
        all_links = []

        craigs_localx_url = craigs_list_url + "/d/free-stuff/search/zip"
        craigs_local_posts = websitepuller.lookup_craigs_posts(craigs_local_url)

        """ Given the free items, see:                      """
        """ 1) How far away?                                """
        """ 2) How much on Ebay                             """
        """ 3) How much for a Lyft                          """

        """ only show me a few items """
        for each_item in craigs_local_posts[0:3]:

            try:
                each_link = each_item.attrs["href"]
                end_lat, end_lng, miles = websitepuller.lookup_miles_from_user(
                each_item, start_lat, start_lng
                )
                # price                  = websitepuller.lookup_price_on_ebay(each_item)
                price = 5

                # mind,maxd              = websitepuller.lookup_cost_lyft(start_lat,start_lng,end_lat,end_lng)
                mind, maxd = 8, 9

                printable_data = (
                    f"{each_item.text} is selling for {price} on "
                    f"Ebay and is {miles:.2f} miles away from you. Using Lyft it will "
                    f"cost between {mind} and {maxd} dollars to pick up.\n"
                )
                all_posts.append(printable_data)
                all_links.append(each_link)

            except AttributeError:
                break

    all_links = enumerate(all_links, start = 1)

    return all_posts, all_links, city, state


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
