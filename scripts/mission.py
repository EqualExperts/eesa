from __future__ import print_function
import sys
import os
import os.path
from thread import start_new_thread

# TODO Nicer way to import bleeding edge libraries?
sys.path.append("/home/apsync/dronekit-python/")
print(sys.path)

import time
from dronekit import connect as drone_connect, mavutil, VehicleMode

class Drone(object):

    def __init__(self, connection_string, release_altitude=50):
        self.connection_string = connection_string
        self.closed_pwm = 1200
        self.open_pwm = 1850
        self.release_servo_number = 9 # aux 1
        self.test_servo_number = 11
        self.release_altitude = release_altitude
        self.current_test_servo_pwm = self.closed_pwm

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

    # Moves servo 9 (aux 1) to release payload
    def release_payload(self):
        print("releasing payload")
        start_new_thread(self.set_servo, (self.release_servo_number, self.open_pwm,))

    # Moves servo 9 (aux 1) to closed to hold payload
    def lock_payload(self):
        print("locking payload")
        start_new_thread(self.set_servo, (self.release_servo_number, self.closed_pwm,))

    # Moves servo 9 (aux 1) to closed to hold payload
    def move_test_servos(self):
        print("moving test servos")
        start_new_thread(self.set_servo, (self.test_servo_number, self.current_test_servo_pwm,))
        if self.current_test_servo_pwm != self.closed_pwm:
            self.current_test_servo_pwm = self.closed_pwm
        else:
            self.current_test_servo_pwm = self.open_pwm

    def connect(self):
        self.connection = drone_connect(self.connection_string, wait_ready=True)
        return self.connection

    def report(self):
        print(" GPS: %s" % self.connection.gps_0)
        print(" Battery: %s" % self.connection.battery)
        print(" Last Heartbeat: %s" % self.connection.last_heartbeat)
        print(" Is Armable?: %s" % self.connection.is_armable)
        print(" System status: %s" % self.connection.system_status.state)
        print(" Mode: %s" % self.connection.mode.name)

    def stop(self):
        return os.path.isfile("/home/apsync/stopmission")

    def autopilot(self):
        # Make sure the payload release is in the closed position
        self.lock_payload()

        # TODO use GPS Fix = 3D before allowing continue?
        # TODO check if safety switch activated?
        while not self.connection.location.global_relative_frame.alt and not self.stop():
            print( "No GPS signal yet" )
            time.sleep(1)

        while not self.stop():
            self.move_test_servos()
            time.sleep(3)

            # Other commands e.g. set flight mode

        self.connection.close()

def start_flight(connection_string):
    drone = Drone(connection_string)
    print("Connecting to plane on %s" % (drone.connection_string,))
    connection = drone.connect()

    timeset = 0

    #TODO maybe only set the system time when GPS quality is good and only set it once?
    @connection.on_message('SYSTEM_TIME')
    def listenerTime(self, name, message):
        if timeset > 40:
            thetime = int(message.time_unix_usec)/1000000
            if sys.platform in ['linux', 'linux2', 'darwin']:
                os.system("sudo date +%s -s @%s" % ('%s', thetime))
            timeset = 0
        timeset += 1

    @connection.on_attribute('GLOBAL_POSITION_INT')
    def listenerGPS(vehicle, name, message):
        alt = message.alt/1000
        print ( "Estimated Altitude %s" % alt )
        if alt >= connection.release_altitude:
            print ( "Releasing payload at %s metres AMSL" % alt)
            connection.release_payload()

    @connection.on_attribute('location.global_frame')
    def listenerPosition(vehicle, name, message):
        alt = message.alt/1000
        print ( "Relative Altitude %s" % alt )
        if alt >= connection.release_altitude:
            print ( "Releasing payload at %s metres relative to home" % alt)
            connection.release_payload()

    drone.report()
    drone.autopilot()

if __name__ == '__main__':
    start_flight('0.0.0.0:9000')

