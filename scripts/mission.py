from __future__ import print_function
import sys
import os
import os.path
from thread import start_new_thread
import time
import math
import random

# TODO Nicer way to import bleeding edge libraries?
sys.path.append("/home/apsync/dronekit-python/")

from dronekit import connect as drone_connect, mavutil, VehicleMode

class Drone(object):

    def __init__(self, connection_string, release_altitude=30000):
        self.connection_string = connection_string
        self.closed_pwm = 1850
        self.open_pwm = 1200
        self.twitch=20
        self.release_servo_number = 9 # aux 1
        self.test_servo_numbers = [11,12,13]
        self.release_altitude = release_altitude
        self.current_test_servo_pwm = self.closed_pwm
        self.released = False

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
    def printlog(self, message):
        print("%s %s" % (time.strftime("%Y %m %d %H:%M:%S", time.gmtime()), message ))

    # Moves servo 9 (aux 1) to release payload
    def release_payload(self):
        self.printlog("!!!!!RELEASING PAYLOAD!!!!!")
        start_new_thread(self.set_servo, (self.release_servo_number, self.open_pwm,))
        self.released = True

    # Moves servo 9 (aux 1) to closed to hold payload
    def lock_payload(self):
        self.printlog("!!!!!LOCKING PAYLOAD!!!!!")
        start_new_thread(self.set_servo, (self.release_servo_number, self.closed_pwm,))
        self.released = False

    # Twitches servo 9 (aux 1) a random amount to keep it warm on the way up
    def twitch_release_servo(self):
        if not self.released:
            min_twitch = self.closed_pwm-self.twitch
            max_twitch = self.closed_pwm+self.twitch
            twitch_pwm = random.randint(min_twitch, max_twitch)
            start_new_thread(self.set_servo, (self.release_servo_number, twitch_pwm))

    # Moves servo 9 (aux 1) to closed to hold payload
    def move_test_servos(self):
        self.printlog("moving test servos")
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
        self.printlog(" GPS: %s" % self.connection.gps_0)
        self.printlog(" Battery: %s" % self.connection.battery)
        self.printlog(" Last Heartbeat: %s" % self.connection.last_heartbeat)
        self.printlog(" Is Armable?: %s" % self.connection.is_armable)
        self.printlog(" System status: %s" % self.connection.system_status.state)
        self.printlog(" Mode: %s" % self.connection.mode.name)

    def stop(self):
        return os.path.isfile("/home/apsync/stopmission")

    def autopilot(self):
        # Make sure the payload release is in the closed position
        self.lock_payload()

        # TODO use GPS Fix = 3D before allowing continue?
        # TODO check if safety switch activated?
        while not self.connection.location.global_relative_frame.alt and not self.stop():
            self.printlog( "No GPS signal yet" )
            time.sleep(1)

        while not self.stop():
            self.move_test_servos()
            time.sleep(3)

            # Other commands e.g. set flight mode

        self.connection.close()

def start_flight(connection_string):
    drone = Drone(connection_string)
    drone.printlog("Connecting to plane on %s" % (drone.connection_string,))
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
                    drone.printlog( "gps time %s" % gpstime )
                    drone.printlog( "sys time %s" % systime )
                    drone.printlog( "diff %s" % difftime )
                    drone.printlog("Setting system time to match GPS")
                    if sys.platform in ['linux', 'linux2', 'darwin']:
                        os.system("sudo date +%s -s @%s" % ('%s', gpstime))
            else:
                drone.printlog( "The GPS returned time since boot instead of time since epoch so can't use it for system time" )

    @connection.on_message('GPS_RAW_INT')
    def listenerRawGps(vehicle, name, message):
        alt = message.alt/1000
        drone.printlog( "GPS RAW Altitude %s" % alt )
        if alt >= drone.release_altitude and not drone.released:
            print ( "Releasing payload at %s metres AMSL RAW" % alt)
            drone.release_payload()
        else:
            drone.twitch_release_servo()

    @connection.on_attribute('GLOBAL_POSITION_INT')
    def listenerGPS(vehicle, name, message):
        alt = message.alt/1000
        drone.printlog( "Estimated Altitude %s" % alt )
        if alt >= drone.release_altitude and not drone.released:
            print ( "%s Releasing payload at %s metres AMSL" % (time.time(),alt))
            drone.release_payload()

    @connection.on_attribute('location.global_frame')
    def listenerPosition(vehicle, name, message):
        alt = message.alt/1000
        drone.printlog( "Relative Altitude %s" % alt )
        if alt >= drone.release_altitude and not drone.released:
            print ( "Releasing payload at %s metres relative to home" % alt)
            drone.release_payload()

    drone.report()
    drone.autopilot()

if __name__ == '__main__':
    start_flight('0.0.0.0:9000')

