import time 
from pprint import pprint


connection_string = '0.0.0.0:9000'

# Import DroneKit-Python
from dronekit import connect, VehicleMode, mavutil

def set_servo(vehicle, servo_number, pwm_value):
	pwm_value_int = int(pwm_value)
	msg = vehicle.message_factory.command_long_encode(
		0, 0, # target system, target component
		mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
		0,
		servo_number,
		pwm_value_int,
		0,0,0,0,0
		)
	vehicle.send_mavlink(msg)

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (connection_string,))
vehicle = connect(connection_string)

# Get some vehicle attributes (state)
print "Get some vehicle attribute values:"
print " GPS: %s" % vehicle.gps_0
print " Battery: %s" % vehicle.battery
print " Last Heartbeat: %s" % vehicle.last_heartbeat
print " Is Armable?: %s" % vehicle.is_armable
print " System status: %s" % vehicle.system_status.state
print " System: %s" % vehicle
print " Mode: %s" % vehicle.mode.name    # settable

pprint(vars(vehicle))
pprint(vars(vehicle.system_status))

vehicle.on_message('*')
def listener(self, name, message):
    print 'message: %s' % message


startalt = vehicle.location.global_frame.alt

for x in xrange(1, 60):
	alt = vehicle.location.global_frame.alt - startalt
	print "Height %s" % alt
	set_servo(vehicle, 1, 1300+x)
	time.sleep(1)

# Close vehicle object before exiting script
vehicle.close()
