from __future__ import print_function
import sys
import os
import os.path
from thread import start_new_thread
import time
import math
import random
import argparse
import logging
from logging.handlers import RotatingFileHandler

# TODO Nicer way to import bleeding edge libraries?
sys.path.append("/home/apsync/dronekit-python/")

from dronekit import connect as drone_connect, mavutil, VehicleMode

class Drone(object):

    def __init__(self, connection_string, release_altitude, relative_altitude):
        self.connection_string = connection_string
        self.closed_pwm = 1890
        self.open_pwm = 1300
        self.twitch=10
        self.release_servo_number = 9 # aux 1
        self.test_servo_numbers = []
        # self.test_servo_numbers = [11,12,13]
        self.release_altitude = release_altitude
        self.relative_altitude = relative_altitude
        self.current_test_servo_pwm = self.closed_pwm
        self.released = False
        self.flight_mission_started = False

	self.home_alt = -1

        logging.basicConfig(format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s')
        self.logger = logging.getLogger('mission_log')
        self.logger.addHandler(RotatingFileHandler('mission.log', maxBytes=10000000, backupCount=0))

    def set_servo(self, servo_number, pwm_value):
        pwm_value_int = int(pwm_value)
        msg = self.connection.message_factory.command_long_encode(
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            servo_number,
            pwm_value_int,
            0, 0, 0, 0, 0
        )
        self.connection.send_mavlink(msg)

    def log(self, message):
        logmessage = "%s %s" % (time.strftime("%Y %m %d %H:%M:%S", time.gmtime()), message )
        self.logger.info(logmessage)
        print(logmessage)

    # Moves servo 9 (aux 1) to release payload
    def release_payload(self):
        self.log("!!!!!RELEASING PAYLOAD!!!!!")
        start_new_thread(self.set_servo, (self.release_servo_number, self.open_pwm,))
        self.released = True
        start_new_thread(self.start_flight_mission, ())

    # Moves servo 9 (aux 1) to closed to hold payload
    def lock_payload(self):
        self.log("!!!!!LOCKING PAYLOAD!!!!!")
        start_new_thread(self.set_servo, (self.release_servo_number, self.closed_pwm,))
        self.released = False


    # Main mission - should be executed after release
    def start_flight_mission(self):
        if not self.flight_mission_started:
            self.flight_mission_started = True
            self.log("Starting flight mission")

            takeoff = VehicleMode("AUTO")
            while self.connection.mode.name != "AUTO":
                self.log("Waiting for AUTO...")
                self.connection.mode = takeoff
                time.sleep(1)

            # Fly somewhere
            # Fly somewhere else
            # Land

    # Twitches servo 9 (aux 1) a random amount to keep it warm on the way up
    def twitch_release_servo(self):
        if not self.released:
            min_twitch = self.closed_pwm-self.twitch
            max_twitch = self.closed_pwm+self.twitch
            twitch_pwm = random.randint(min_twitch, max_twitch)
            start_new_thread(self.set_servo, (self.release_servo_number, twitch_pwm))

    # Moves servo 9 (aux 1) to closed to hold payload
    def move_test_servos(self):
        self.log("moving test servos")
        for servo_number in self.test_servo_numbers:
            start_new_thread(self.set_servo, (servo_number, self.current_test_servo_pwm,))
        if self.current_test_servo_pwm != self.closed_pwm:
            self.current_test_servo_pwm = self.closed_pwm
        else:
            self.current_test_servo_pwm = self.open_pwm

    def connect(self):
        self.connection = drone_connect(self.connection_string, wait_ready=True)
        return self.connection

    def report(self):
        self.log(" GPS: %s" % self.connection.gps_0)
        self.log(" Battery: %s" % self.connection.battery)
        self.log(" Last Heartbeat: %s" % self.connection.last_heartbeat)
        self.log(" Is Armable?: %s" % self.connection.is_armable)
        self.log(" System status: %s" % self.connection.system_status.state)
        self.log(" Mode: %s" % self.connection.mode.name)

    def stop(self):
        return os.path.isfile("/home/apsync/stopmission")

    def release_now(self):
        return os.path.isfile("/home/apsync/releasenow")

    def autopilot(self):

        # TODO use GPS Fix = 3D before allowing continue?
        # TODO check if safety switch activated?
        while not self.connection.is_armable and not self.stop():
            self.log( "Initialising...." )
            time.sleep(5)

	self.log("Desired release altitude = %s" % self.release_altitude )

        # Make sure the payload release is in the closed position
        self.lock_payload()

	while not self.connection.armed and not self.stop():
	    self.log( "Waiting for aircraft to be armed...." )
            time.sleep(5)

        while not self.stop():
            if self.release_now():
                self.release_payload()
                time.sleep(10)
                break;
            self.move_test_servos()
            time.sleep(3)

        logging.shutdown()
        self.connection.close()

def start_flight(connection_string, release_altitude=100, relative_altitude=True):
    drone = Drone(connection_string, release_altitude, relative_altitude)
    drone.log("Connecting to plane on %s" % (drone.connection_string,))
    connection = drone.connect()
    nowish = 1501926112 # Aug 5th 2017

    @connection.on_message('SYSTEM_TIME')
    def listenerTime(vehicle, name, message):
        if connection.gps_0.fix_type == 3:
            gpstime = int(message.time_unix_usec)/1000000
            systime = int(time.time())

            if gpstime > nowish:
                difftime = math.fabs(gpstime - systime)
                if difftime > 60:
                    drone.log( "gps time %s" % gpstime )
                    drone.log( "sys time %s" % systime )
                    drone.log( "diff %s" % difftime )
                    drone.log("Setting system time to match GPS")
                    if sys.platform in ['linux', 'linux2', 'darwin']:
                        os.system("sudo date +%s -s @%s" % ('%s', gpstime))
            else:
                drone.log( "The GPS returned time since boot instead of time since epoch so can't use it for system time" )

    @connection.on_message('GPS_RAW_INT')
    def listener_raw_gps(vehicle, name, message):
        alt = message.alt/1000
        drone.log( "RAW Alt %s" % alt )
        if alt >= drone.release_altitude and not drone.released:
            drone.log ( "Releasing payload at %s metres AMSL RAW" % alt)
            drone.release_payload()

    @connection.on_attribute('GLOBAL_POSITION_INT')
    def listener_gps(vehicle, name, message):
        alt = message.alt/1000
        drone.log( "Est Alt %s" % alt )
        if alt >= drone.release_altitude and not drone.released:
            drone.log ( "%s Releasing payload at %s metres AMSL" % (time.time(),alt))
            drone.release_payload()

    @connection.on_attribute('location.global_frame')
    def listener_position(vehicle, name, message):
        alt = message.alt
	if drone.home_alt == -1:
	    drone.home_alt = alt
	    drone.log("Set home alt to %s" % drone.home_alt)
	rel_alt = alt - drone.home_alt
	ts = int(time.time()*10)
	if ts % 10 == 0:
            drone.log( "Rel Alt %s" % rel_alt )
        if rel_alt >= drone.release_altitude and not drone.released:
            drone.log ( "Releasing payload at %s metres relative to home" % rel_alt)
            drone.release_payload()
        else:
            drone.twitch_release_servo()

    drone.report()
    drone.autopilot()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Space Mission!!')
    parser.add_argument('--altitude',
                   help="Target release altitude defaults to 100m.", default=100,type=int)
    parser.add_argument('--relative',
                   help="Altitude above home location.  Good for field testing", action="store_true");
    parser.add_argument('--connection',
                   help="Connection string to use for pixhawk or sitl connection", default="0.0.0.0:9000");
    args = parser.parse_args()

    target_altitude = args.altitude
    relative_altitude = args.relative
    connection = args.connection

    print( "Target alt = %s, relative to home? %s" % (target_altitude, relative_altitude) )

    start_flight(connection, target_altitude, relative_altitude)

