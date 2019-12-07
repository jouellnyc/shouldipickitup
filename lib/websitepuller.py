#!/home/john/anaconda3/bin/python3.7


try:
    import re
    import sys

    from bs4 import BeautifulSoup
    from geopy.distance import geodesic

    from . import requestwrap
except Exception as e:
    print("died in web ", e)

def lookup_craigs_posts(craigs_list_url):
    craigs_response = requestwrap.err_web(craigs_list_url)
    craigs_soup  = BeautifulSoup(craigs_response.text, 'html.parser')
    craigs_posts = craigs_soup.find_all('a', class_= 'result-title hdrlnk')
    return craigs_posts

mapsre = re.compile("https://www.google.com/maps/preview/")

def lookup_miles_from_user(each_item,start,end):
    item_url          = each_item.attrs['href']
    craigs_resp       = requestwrap.err_web(item_url)
    craigs_soup       = BeautifulSoup(craigs_resp.text, 'html.parser')
    googurl           = craigs_soup.find('a', href=mapsre)

    try:
        lat,lon, _        = googurl.attrs['href'].split('@')[1].split('z')[0].split(',')
    except AttributeError:
        print(f"{each_item.text} was likely deleted")
        pass
    miles             = geodesic((start,end),(lat,lon)).mi
    return miles

def lookup_price_on_ebay(each_item):
    ebay_path      = f"{each_item.text}&_sacat=0&LH_TitleDesc=0&_osacat=0&_odkw={each_item.text}"
    ebay_query_url = ebay_url + ebay_path
    ebay_resp      = requestwrap.err_web(ebay_query_url)
    ebay_soup      = BeautifulSoup(ebay_resp.text, 'html.parser')
    #print("soup eb: " + str( len(ebay_soup) ) )
    try:
        item           = ebay_soup.find("h3", {"class": "s-item__title"}).get_text(separator=u" ")
    except AttributeError:
        item = "no match"
        price = "no price"
        return price
    #print("soup i: " + str( len(item)      ) )
    #print("eb: " + item)
    try:
        price          = ebay_soup.find("span", {"class": "s-item__price"}).get_text()
    except AttributeError:
        price = "no price"
        return price


lyft_url     = "http://www.lyft.com"
ebay_url     = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="

if __name__ == "__main__":
    pass
