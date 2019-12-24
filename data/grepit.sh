#!/bin/bash


FILE1="cities.txt"
FILE2="free-zipcode-database-Primary.no.header.csv"
FILE3="zips2cities.txt"


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
