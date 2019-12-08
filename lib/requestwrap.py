 #!/home/john/anaconda3/bin/python3.7


''' wrap repetitive web requests ''' 

import sys
import requests

""" Functions """
def err_web(url):
    """ Catch the Errors from the Web Connections             """
    """ All or nothing here: If not 200 OK - exit the program """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 '
            'Safari/537.36'
        }
        r = requests.get(url, timeout=10,
                         allow_redirects=True, headers=headers)
        #raise_for_status() never execs if request.get above has connect error/timeouts
        r.raise_for_status()
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
        return r
