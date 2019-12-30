

#while read x; do  ./lib/testmemached.py "$x"; done < data/zip_codes.txt | grep -ioE [\'[a-z]+,.*\'[A-Z]+\' | sort | sed 's/ //g' |cut -d \' -f2,4 | tr \' , >> data/cities_with_links_from_memcached.txt


while read x; do  echo == $x ==;  ./lib/testmemached.py "$x"; done < data/cities_with_links_from_memcached.txt

#while read x; do  echo == $x ==;  ./lib/testmemached.py "$x"; done < data/zip_codes.txt
