#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../scripts")
import mission
from dronekit import connect as drone_connect, mavutil, VehicleMode

#Connect to remote SITL instance
connection_string = "udp:127.0.0.1:5769"

vehicle = drone_connect(connection_string, wait_ready=True)
while not vehicle.location.global_frame.alt and not self.stop():
    self.log( "No GPS signal yet" )
    time.sleep(1)
current_alt=vehicle.location.global_frame.alt
release_alt=current_alt+100
print("Current altitude = %s so release altitude = %s" % (current_alt, release_alt))
vehicle.close()

mission.start_flight(connection_string, release_alt)

