#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib import websitepuller
from lib import govzipsandcities
from lib import craigzipsandurls

zip_code_file = "/home/john/gitrepos/shouldipickitup/data/free-zipcode-database-Primary.no.header.csv"


def main(zip):

    start_lat = "40.6490763"
    start_lng = "-73.9762069"

    start_lat = "29.5964"
    start_lng = "-82.2178"

    """ Given a zip, find the closest numerial match and return city,state names """
    try:
        return (
            craigzipsandurls.lookup_items_in_zip_memcached(zip),
            ["a", "b", "c"],
            "b",
            "c",
        )
    except ValueError:
        try:
            city, state = govzipsandcities.lookup_city_state_given_zip_memcached(zip)
            citytext = f"{city},{state}"  # Add the comman back in...
            print(f"Debug citytext: {citytext}\n" f"city: {city}\n" f"state:{state}")
        except ValueError:
            citytext = "SFbayarea"
            city = f"Couldn't find anything near {zip}, but here's Bay Area "
            state = ""
        except ConnectionRefusedError:
            city, state = govzipsandcities.lookup_city_state_given_zip_file(
                zip, zip_code_file
            )
            city, state = city.lower(), state.upper()
            citytext = f"{city},{state}"
            # print(f"Debug citytext: {citytext}, {city}, {state}, {citytext}")

    """ Given a city name, find the closest local Craigslist Url """
    try:
        craigs_list_url = craigzipsandurls.lookup_craigs_url_memcached(citytext)
        craigs_list_url = craigs_list_url.decode("UTF-8")
    except ValueError as e:
        print("veeqq", type(e), e)
        craigs_list_url = "https://sfbay.craigslist.org"  # no trailing /
        city = f"Couldn't find anything near {zip}, but here's Bay Area "
        state = ""
        print(craigs_list_url)
    except ConnectionRefusedError:
        try:
            print("h1")
            web_links = craigzipsandurls.create_craigs_url_dict_from_disk()
            craigs_list_url = craigzipsandurls.lookup_craigs_url_from_dict_file(
                citytext, web_links
            )
            print("h1a")
        except KeyError:
            print("KE:")
            citytext = "SFbayarea"
            craigs_list_url = "https://sfbay.craigslist.org"  # no trailing /
            city = f"Couldn't find anything near {zip}, but here's Bay Area "
            state = ""
            print(f"Debug url: {craigs_list_url}")
            print(city, state, citytext)
    except Exception as e:
        print("eeeeeeqq", type(e), e)
        # else:
        # print(f"Debug: {citytext} is available at {craigs_list_url}")

    """ Given the the closest local Craigslist url, return the free items """
    print("h2")
    craigs_local_url = craigs_list_url + "/d/free-stuff/search/zip"
    print("h3")
    craigs_local_posts = websitepuller.lookup_craigs_posts(craigs_local_url)

    """ Given the free items, see:                      """
    """ 1) How far away?                                """
    """ 2) How much on Ebay                             """
    """ 3) How much for a Lyft                          """

    """ only show me a few items """

    all_posts = []
    all_links = []

    for each_item in craigs_local_posts[0:3]:

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
    all_links = enumerate(all_links, 1)
    return all_posts, all_links, city.capitalize(), state.upper()


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
