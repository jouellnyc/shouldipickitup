#!/home/john/anaconda3/bin/python3.7
#http://federalgovernmentzipcodes.us/download.html

''' Build and load zip code data into a file or memcached and '''
''' make available functions to return that data              '''

try:
    import re
    import csv
    from pymemcache.client import base
except Exception as e:
    print("died in gov ", e)

zip_code_file = ('/home/john/gitrepos/shouldipickitup/data/free-zipcode-database-Primary.no.header.csv')

def create_zips_city_state_dict_from_file(zip_code_file):
    ''' Return a dictionary with zip : (city,state) tuples '''
    try:
        with open(zip_code_file) as csv_fh:

            csv_reader = csv.reader(csv_fh, delimiter=',')
            myzips = {}

            for row in csv_reader:
                zip   = row[0]
                city  = row[2]
                state = row[3]
                myzips[zip] = (city,state)

        return myzips
    except Exception as e:
        return None

def load_zips_to_memcached(zipcode_dict):
    ''' write all the key/values to memcached '''
    client = base.Client(('localhost', 11211))
    for zip,(city,state) in zipcode_dict.items():
        print(zip,(city,state))
        client.set(zip,(city,state))

def lookup_city_state_given_zip(zip):
    ''' Given a zipcode and the zipcode dictionary return closest city,state '''
    ''' as a tuple. If no hit, find the closest and cache that in memcached  '''
    client = base.Client(('localhost', 11211))
    closest = client.get(zip)
    #No hit
    if closest is None:
        #Create zip db via file
        myzips  = create_zips_city_state_dict_from_file(zip_code_file)
        print('file')
        closest = myzips[min(myzips.keys(), key=lambda k: abs(int(k)-int(zip)))]
        city, state = closest
        #Add the nearest city,zip to the fast memcached cache
        client.set(zip,(city,state))
        #print(zip,(city,state))
        return (city,state)
    #Hit!
    else:
        city, state = closest.decode("utf-8").split(',')
        patt  = re.compile('\w+')
        city  = patt.search(city).group()
        state = patt.search(state).group()
        return (city.lower(),state)

if __name__ == "__main__":
    zipcode_dict = create_zips_city_state_dict_from_file(zip_code_file)
    if zipcode_dict is None:
        pass
        print("create_zips_city_state_dict_from_file failed")
    else:
        load_zips_to_memcached(zipcode_dict)
