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

    def __init__(self, connection_string, release_altitude=10):
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

    def autopilot(self):
        # Make sure the payload release is in the closed position
        self.lock_payload()

        # Calculate relative altitude only for low level tests.
        # WARNING This can't be used for long duration flights in-case the script restarts
        startalt = None
        while not startalt:
            time.sleep(1)
            startalt = self.connection.location.global_frame.alt

        stop = False

        while not stop:
            alt = self.connection.location.global_frame.alt - startalt
            print ( "Height %s" % alt )
            if alt >= self.release_altitude:
                self.release_payload()
                time.sleep(2)
            self.move_test_servos()
            time.sleep(3)
            if os.path.isfile("/home/apsync/stopmission"):
                stop = True

        # Other commands e.g. set flight mode

        self.connection.close()

def start_flight(connection_string):
    drone = Drone(connection_string)
    print("Connecting to plane on %s" % (drone.connection_string,))
    connection = drone.connect()

    @connection.on_message('SYSTEM_TIME')
    def listener(self, name, message):
        thetime = int(message.time_unix_usec)/1000000
        if sys.platform in ['linux', 'linux2', 'darwin']:
            os.system("sudo date +%s -s @%s" % ('%s', thetime))

    drone.report()
    drone.autopilot()

if __name__ == '__main__':
    start_flight('0.0.0.0:9000')