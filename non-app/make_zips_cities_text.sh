#!/bin/bash

#Given this site: https://geo.craigslist.org/iso/us
#find the city, state pairs with commas (not shown)
FILE1="cities.txt"
#also see cities_commas.txt

#Govt file with zips and city/states names
FILE2="../data/free-zipcode-database-Primary.no.header.csv"

#Match output file
FILE3="zips2cities.txt"

#Massage FILE3 to get 'cities.txt'
while IFS=, read -r CITY STATE
do

    STATE=$(echo ${STATE} | tr a-z A-Z)
    if grep -iq "${CITY}" $FILE2 ; then
        ZIP=$(grep -i "${CITY}" $FILE2 | grep "${STATE}" | grep STANDARD  | head -n 1 | cut -d ',' -f 1)
        echo  -n "${CITY},${STATE} is at ${ZIP}"
    else
        echo  -n "${CITY} ${STATE}: nomatch"
    fi
    echo

done < $FILE1  | grep -iv nomatch > "${FILE3}"
