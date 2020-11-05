
# Historical Stock Data (With Growth Rates) 
![Stocks](stock_peek.gif)

## Installing Locally
```
git clone https://github.com/ShouldIPickItUp/Stocks
cd Stocks
docker-compose -f docker-compose.local.yaml  up -d
```

### Setup 
```
Enter the flask container and start crawling:

 ./non-app/master.enter.sh flask

nobody@cb9eb7ca0e0b:/$ /stocks/lib/crawler.py -s GOOG
Retrieving HTML for  GOOG
Parsing HTML
Pulling Data out of HTML

GOOG had 73,590.0 M Revenue in 2015 4 GR Rate =  21.69%
<szip>

The DB 'Stocks' will be auto created in the local Mongo Container

./non-app/master.enter.sh mongodb 

> show dbs
Stocks  0.000GB
admin   0.000GB
config  0.000GB
local   0.000GB

Point your browser to http://$YOUR_IP and search for GOOG or 
http://$YOUR_IP/search/?stock=GOOG

```

## Architechure
Nginx will listen on the local hosts port 80

Flask and Mongodb will be on the same bridged docker network reachable by docker names

## Requirements
git/docker/docker-compose/optionally a MongoDB hosted at Mongo

## Contributing
1. Fork it (<https://github.com/ShouldIPickItUp/Stock>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
