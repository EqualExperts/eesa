from __future__ import print_function
from threading import Timer
import sys
import Thread

# TODO Nicer way to import bleeding edge libraries?
sys.path.append("/home/apsync/dronekit-python/")
print(sys.path)

import time
from dronekit import connect, VehicleMode, mavutil

# TODO Setup SITL so it can be tested locally instead of on the Pixhawk
connection_string = '0.0.0.0:9000'
closed_pwm = 1000
open_pwm = 1800
servo_number = 9  # aux 1
release_altitude = 100  # metres, for toy glider


# release_altitude = 400 # metres, for actual plane testing
# release_altitude = 30000 # metres, for record attempt

# Generic Set Servo function
# TODO Maybe move these mission specific functions out to eesa library?
def set_servo(pwm_value):
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
    Thread.start_new_thread(set_servo(open_pwm))


# Moves servo 9 (aux 1) to closed to hold payload
def lock_payload():
    Thread.start_new_thread(set_servo(open_pwm))


print("Connecting to plane on %s" % (connection_string,))
vehicle = connect(connection_string)

print(" GPS: %s" % vehicle.gps_0)
print(" Battery: %s" % vehicle.battery)
print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
print(" Is Armable?: %s" % vehicle.is_armable)
print(" System status: %s" % vehicle.system_status.state)
print(" Mode: %s" % vehicle.mode.name)

# Make sure the payload release is in the closed position
lock_payload(vehicle)

# Calculate relative altitude only for low level tests.
# WARNING This can't be used for long duration flights in-case the script restarts
startalt = vehicle.location.global_frame.alt
released = False

while not released:
    alt = vehicle.location.global_frame.alt - startalt
    print
    "Height %s" % alt
    if alt >= release_altitude:
        release_payload()
        released = True
    time.sleep(1)

# Other commands e.g. set flight mode

vehicle.close()
