#! /bin/bash

LOGGER_HOME="%(home)s"
ID="%(id)s"

while true
do
  timeout -s 9 %(timeout)s curl $LOGGER_HOME/rpi/$ID
  sleep %(interval)s
done
