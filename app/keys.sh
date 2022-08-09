#!/bin/sh

while getopts ":r:" opt; 
do
  case $opt in
    r) arg_1="$OPTARG";;
  esac
done

openssl ecparam -name prime256v1 -genkey -noout -out $arg_1/vapid_private.pem
openssl ecparam -name prime256v1 -genkey -noout -out $arg_1/vapid_secret.pem

openssl ec -in $arg_1/vapid_private.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' >> $arg_1/private.txt
openssl ec -in $arg_1/vapid_private.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' >> $arg_1/public.txt

openssl ec -in $arg_1/vapid_secret.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' >> $arg_1/secret
openssl ec -in $arg_1/vapid_secret.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' >> $arg_1/apikey
