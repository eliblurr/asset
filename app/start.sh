#!/bin/bash

workers=1
server=uvicorn
extra=

while getopts ":s:w:e:" opt; do
  case $opt in
    s) server="$OPTARG";;
    w) workers="$OPTARG";;
    e) extra="$OPTARG";;
  esac
done

echo $args

echo "[STARTING COMMAND]:${server} main:app --workers ${workers} ${extra}"
eval "${server} main:app --workers ${workers} ${extra}"
