from __future__ import print_function
from threading import Timer
import sys
import os
import os.path
from thread import start_new_thread

# TODO Nicer way to import bleeding edge libraries?
sys.path.append("/home/apsync/dronekit-python/")
print(sys.path)

import time
from dronekit import connect, VehicleMode, mavutil

# TODO Setup SITL so it can be tested locally instead of on the Pixhawk
# connection_string = '0.0.0.0:14550' # sitl
connection_string = '0.0.0.0:9000' # onboard Edison

closed_pwm = 1850
open_pwm = 1200
release_servo_number = 9  # aux 1
test_servo_number = 11

release_altitude = 10  # metres, for toy glider
# release_altitude = 400 # metres, for actual plane testing
# release_altitude = 30500 # metres, for record attempt

current_test_servo_pwm = closed_pwm

# Generic Set Servo function
# TODO Maybe move these mission specific functions out to eesa library?
def set_servo(servo_number, pwm_value):
    pwm_value_int = int(pwm_value)
    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,
        servo_number,
        pwm_value_int,
        0, 0, 0, 0, 0
    )
    vehicle.send_mavlink(msg)

# Moves servo 9 (aux 1) to release payload
def release_payload():
    print("releasing payload")
    start_new_thread(set_servo, (release_servo_number, open_pwm,))

# Moves servo 9 (aux 1) to closed to hold payload
def lock_payload():
    print("locking payload")
    start_new_thread(set_servo, (release_servo_number, closed_pwm,))

# Moves servo 9 (aux 1) to closed to hold payload
def move_test_servos():
    global current_test_servo_pwm
    print("moving test servos")
    start_new_thread(set_servo, (test_servo_number, current_test_servo_pwm,))
    if current_test_servo_pwm != closed_pwm:
        current_test_servo_pwm = closed_pwm
    else:
        current_test_servo_pwm = open_pwm

print("Connecting to plane on %s" % (connection_string,))
vehicle = connect(connection_string)

@vehicle.on_message('SYSTEM_TIME')
def listener(self, name, message):
    thetime = int(message.time_unix_usec)/1000000
    os.system("sudo date +%s -s @%s" % ('%s', thetime))

print(" GPS: %s" % vehicle.gps_0)
print(" Battery: %s" % vehicle.battery)
print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
print(" Is Armable?: %s" % vehicle.is_armable)
print(" System status: %s" % vehicle.system_status.state)
print(" Mode: %s" % vehicle.mode.name)

# Make sure the payload release is in the closed position
lock_payload()

# Calculate relative altitude only for low level tests.
# WARNING This can't be used for long duration flights in-case the script restarts
startalt = vehicle.location.global_frame.alt
stop = False

while not stop:
    alt = vehicle.location.global_frame.alt - startalt
    print ( "Height %s" % alt )
    if alt >= release_altitude:
        release_payload()
        time.sleep(2)
    move_test_servos()
    time.sleep(3)
    if os.path.isfile("/home/apsync/stopmission"):
        stop = True

# Other commands e.g. set flight mode

vehicle.close()
