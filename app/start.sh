#!/bin/bash

workers=1
server=gunicorn
extra=
redis_workers=4

while getopts ":s:w:e:p:" opt; do
  case $opt in
    s) server="$OPTARG";;
    w) workers="$OPTARG";;
    e) extra="$OPTARG";;
    p) redis_workers="$OPTARG";;
  esac
done

echo "Spawning ${redis_workers} workers"
for (( i=1; i<=$redis_workers; i++))
do
  python3 -m rds.worker & 
done

echo "[STARTING COMMAND]:${server} main:app --workers ${workers} ${extra}"
eval "${server} main:app --workers ${workers} ${extra}"

