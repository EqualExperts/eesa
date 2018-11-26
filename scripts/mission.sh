#!/bin/sh
sleep 1m
cd /home/apsync
gzip -c mission.log  > mission.log."$(date +%s)".gz;
gzip -c flight.log  > flight.log."$(date +%s)".gz;
until [ -f /home/apsync/stopmission ]
do
  rm -f releasenow stopmission
  python mission.py 2>&1 >> /tmp/mission.log
  sleep 5
done
