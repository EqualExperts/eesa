#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
from pymavlink import mavutil
<<<<<<< HEAD
from math import sin, cos, sqrt, atan2, radians
=======
>>>>>>> 442e5e4f4c372560724fba84af694ca7afa7e967
import time
import json
# import dronekit_sitl

#Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
parser.add_argument('--landing_sites_file',
                    help="A file containing a json list of landing sites.  Defaults to landing_sites.json")
parser.add_argument('--benchtest',
                    help="Run as a sitl script", action="store_true");
args = parser.parse_args()

connection_string = args.connect
benchtest = args.benchtest
landing_sites_file = args.landing_sites_file

if not connection_string:
    connection_string = "/dev/serial0"

if not landing_sites_file:
    landing_sites_file = "landing_sites.json"

# sitl = dronekit_sitl.start_default()
# connection_string = sitl.connection_string()
if benchtest:
    print("Running benchtest script to connect to SITL")
    connection_string = "udp:127.0.0.1:5769"

# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True, baud=57600)

def wait_for_rtl():
    """
    Waits for RTL mode before injecting mission with nearest safe landing area
    """

    print " Waiting for mode change ..."
    while not vehicle.mode.name=='RTL':  #Wait until mode has changed
        time.sleep(1)

def switch_to_rtl():
    vehicle.mode = VehicleMode("GUIDED")
    while not vehicle.mode.name=='GUIDED':  #Wait until mode has changed
        time.sleep(1)
    print "Returning to alternate landing site"
    vehicle.mode = VehicleMode("RTL")

def calculate_nearest_safe_landing():
    landing_sites = json.load(landing_sites_file)

    distance = get_distance_to_home()
    chosen_site = None

    for site in landing_sites["sites"]:
<<<<<<< HEAD
        site_distance = get_distance(site["lat"], site["lon"])
=======
        site_distance = get_distance(site)
>>>>>>> 442e5e4f4c372560724fba84af694ca7afa7e967
        if site_distance < distance:
            distance = site_distance
            chosen_site = site

    return chosen_site

<<<<<<< HEAD
def get_distance_to_home():
    home = vehicle.home_location
    return get_distance(home.lat, home.lon)

def get_distance(latitude, longitude):
    current = vehicle.location.global_relative_frame
    R = 6373.0

    lat1 = radians(current.lat)
    lon1 = radians(current.lon)
    lat2 = radians(latitude)
    lon2 = radians(longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    print( "Distance = %s" % distance)
    return distance

=======
>>>>>>> 442e5e4f4c372560724fba84af694ca7afa7e967
def inject_landing_mission(site):
    if site is not None:
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready()

        cmds.clear()

        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL, mavutil.mavlink.MAV_CMD_DO_LAND_START, 0, 1, 0, 0, 0, 0, site["start"]["lat"], site["start"]["lon"], site["start"]["alt"])
        cmds.add(cmd)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0, site["land"]["lat"], site["land"]["lon"], site["land"]["alt"])
        cmds.add(cmd)

        cmds.upload()

<<<<<<< HEAD

=======
>>>>>>> 442e5e4f4c372560724fba84af694ca7afa7e967
wait_for_rtl()
site = calculate_nearest_safe_landing()
if site is not None:
    print("Switching to alternative landing site %s" % site["id"])
    inject_landing_mission(site)
    switch_to_rtl()
else:
    print("Home is nearest landing site so continuing default RTL")


#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

