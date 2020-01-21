#!/usr/bin/env python3

""" requestwrap.py -  wrap repetitive web requests

- This script module:
    - uses requests to screen scrape and serves as a wrapper for requests
    - takes in a url and crawls it

-This script requires the requests module.

-This file is meant to be imported as a module.

- It contains the following functions:
    * err_web- the main function of the script wrapping requests

"""

import sys
import requests
import random


def err_web(url):
    """
    Catch the Errors from the Web Requests
    All or nothing here: If not 200 OK - exit the program

    Parameters
    ----------
    url : str
        The URL to crawl

    Returns
    -------
    httprequest :  A  Beautiful Soup object
    """
        #Windows 10-based PC using Edge browser
        #Mac OS X-based computer using a Safari browser
    user_agents = [

                {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                "AppleWebKit/537.36 (KHTML, like Gecko)" 
                "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"},

                {"User-Agent": "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 "
                "(KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"}

                ]

    print(random.choice(user_agents))

    try:
        httprequest = requests.get(
            url, timeout=10, allow_redirects=True, headers=random.choice(user_agents)
        )
        # raise_for_status() never execs if requests.get above has connect error/timeouts
        httprequest.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Fatal Error Connecting:", errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        sys.exit(1)
    else:
        return httprequest

err_web('http://www.google.com')
