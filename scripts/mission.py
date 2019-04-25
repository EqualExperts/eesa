from __future__ import print_function
import sys
import signal
import os
import os.path
from thread import start_new_thread
import time
import math
import random
from flight import Flight
from log import FlightLog
import json

from dronekit import connect as drone_connect, mavutil, VehicleMode

class Drone(object):

	def __init__(self, connection_string):
		self.mission_parameters = self.load_mission_parameters()
		print( json.dumps(self.mission_parameters))
		self.aircraft = self.load_aircraft_configuration()
		self.connection_string = connection_string
		signal.signal(signal.SIGINT, self.shutdown)
		signal.signal(signal.SIGTERM, self.shutdown)
		self.stopped = False
		self.current_test_servo_pwm = self.aircraft['closed_pwm']
		self.released = False
		self.flight_mission_started = False

		self.flight = None
		self.connection = None

		self.log = FlightLog('mission.log')

	def load_mission_parameters(self):
		with open('../locations/penicuik-penicuik.json', 'r') as f:
			return json.load(f)

	def load_aircraft_configuration(self):
		with open('../aircraft/skyhunter.json', 'r') as f:
			return json.load(f)

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
		self.log.logInfo(self.connection, "!!!!!RELEASING PAYLOAD!!!!!")
		start_new_thread(self.set_servo, (self.aircraft['release_servo_number'], self.aircraft['open_pwm'],))
		self.released = True
		if not self.flight_mission_started:
			self.flight_mission_started = True
			start_new_thread(self.start_flight_mission, ())

	# Moves servo 9 (aux 1) to closed to hold payload
	def lock_payload(self):
		self.log.logInfo(self.connection, "!!!!!LOCKING PAYLOAD!!!!!")
		start_new_thread(self.set_servo, (self.aircraft['release_servo_number'], self.aircraft['closed_pwm'],))
		self.released = False


	# Main mission - should be executed after release
	def start_flight_mission(self):
		self.flight = Flight(self.connection, self.mission_parameters)
		self.flight.takeoff()

	# Twitches servo 9 (aux 1) a random amount to keep it warm on the way up
	def twitch_release_servo(self):
		if not self.released:
			min_twitch = self.closed_pwm-self.twitch
			max_twitch = self.closed_pwm+self.twitch
			twitch_pwm = random.randint(min_twitch, max_twitch)
			start_new_thread(self.set_servo, (self.release_servo_number, twitch_pwm))

	# Moves servo 9 (aux 1) to closed to hold payload
	def move_test_servos(self):
		if not self.released:
			self.log.logDebug(self.connection, "moving test servos")
			for servo_number in self.aircraft['test_servo_numbers']:
				start_new_thread(self.set_servo, (servo_number, self.current_test_servo_pwm,))
			if self.current_test_servo_pwm != self.aircraft['closed_pwm']:
				self.current_test_servo_pwm = self.aircraft['closed_pwm']
			else:
				self.current_test_servo_pwm = self.aircraft['open_pwm']

	def connect(self):
		self.connection = drone_connect(self.connection_string, wait_ready=True)
		return self.connection

	def release_now(self):
		path = os.path.dirname(os.path.abspath(__file__) )
		return os.path.isfile("%s/releasenow" % path)

	def autopilot(self):

		# TODO use GPS Fix = 3D before allowing continue?
		# TODO check if safety switch activated?
		while not self.connection.is_armable and not self.stopped:
			self.log.logInfo(self.connection, "Initialising...." )
			time.sleep(5)

		self.release_altitude = self.mission_parameters['launch']['altitude'] + self.mission_parameters['release']['height']

		self.log.logInfo(self.connection, "Desired release altitude = %s" % self.release_altitude )

		# Make sure the payload release is in the closed position
		self.lock_payload()

		while not self.stopped:
			self.move_test_servos()
			time.sleep(3)

		self.shutdown()

	def shutdown(self, a, b):
			self.stopped = True
			self.log.report(self.connection)
			self.log.logInfo(self.connection, "Mission script complete")
			if self.connection != None:
				self.connection.close()
			self.log.shutdown()
			print("Mission script complete")
			sys.exit()

def start_flight(connection_string):
	drone = Drone(connection_string)
	drone.log.logInfo(drone.connection, "Connecting to plane on %s" % (drone.connection_string,))
	connection = drone.connect()
	nowish = 1501926112 # Aug 5th 2017

	# Default mode before target is RTL, just incase of an early release
	connection.mode = VehicleMode("RTL")

	@connection.on_message('SYSTEM_TIME')
	def listenerTime(vehicle, name, message):
		if connection.gps_0.fix_type == 3:
			gpstime = int(message.time_unix_usec)/1000000
			systime = int(time.time())

			if gpstime > nowish:
				difftime = math.fabs(gpstime - systime)
				if difftime > 60:
					drone.log.logInfo(drone.connection, "gps time %s" % gpstime )
					drone.log.logInfo(drone.connection, "sys time %s" % systime )
					drone.log.logInfo(drone.connection, "diff %s" % difftime )
					drone.log.logInfo(drone.connection, "Setting system time to match GPS")
					if sys.platform in ['linux', 'linux2', 'darwin']:
						os.system("sudo date +%s -s @%s" % ('%s', gpstime))
			else:
				drone.log.logInfo(drone, "The GPS returned time since boot instead of time since epoch so can't use it for system time" )

	@connection.on_attribute('location.global_frame')
	def listener_position(vehicle, name, message):
		alt = message.alt
		rel_alt = alt - drone.mission_parameters['launch']['altitude']
		ts = int(time.time()*10)
		if ts % 25 == 0:
			drone.log.logInfo(drone.connection, "Rel Alt %s" % rel_alt )
		if drone.flight:
			drone.flight.alt = alt
			drone.flight.lng = message.lon
			drone.flight.lat = message.lat	
		if not drone.released and alt >= drone.release_altitude:
			drone.log.logInfo(drone.connection, "Releasing payload at %s metres relative to home" % rel_alt)
			drone.release_payload()
		elif not drone.released and drone.release_now():
			drone.log.logInfo(drone.connection, "Forced Releasing payload at %s metres relative to home" % rel_alt)
			drone.release_payload()
		else:
			drone.twitch_release_servo()

	drone.log.report(drone.connection)
	drone.autopilot()

if __name__ == '__main__':
	start_flight('0.0.0.0:9000')

