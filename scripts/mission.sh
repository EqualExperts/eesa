#!/bin/sh
# sleep 3m
cd /home/apsync
until [ -f /home/apsync/stopmission ]
do
  gzip -c mission.log  > mission.log."$(date +%s)".gz;
  python mission.py 2>&1 > mission.log
  sleep 5
done
# TODO loop unless stopmission found incase wait timeout?
