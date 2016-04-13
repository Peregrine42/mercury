#! /bin/bash

while true
do
  timeout -s 9 %(timeout)s /home/mercury/sync.sh
  sleep %(interval)s
done
