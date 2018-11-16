from __future__ import print_function
import sys
import os
import os.path
from thread import start_new_thread
import time
import math
import random
from flight import Flight

import logging
from logging.handlers import RotatingFileHandler

# TODO Nicer way to import bleeding edge libraries?
sys.path.append("/home/apsync/dronekit-python/")

from dronekit import connect as drone_connect, mavutil, VehicleMode

class Drone(object):

	# Iceland
	#home = { 'lat': 123.456, 'lng': 567.890, 'alt': 90, 'release_alt': 30000 }
	# Devils Beef Tub
	# home = { 'lat': 55.404, 'lng': -3.486, 'alt': 440, 'release_alt': 440 }
	# Penicuik
	home = { 'lat': 55.807, 'lng': -3.248, 'alt': 302, 'release_alt': 302 }
	# Otley Road
	# home = { 'lat': 53.880447, 'lng': -1.795451, 'alt': 312, 'release_alt': 312 }

	def __init__(self, connection_string):
		self.connection_string = connection_string
		self.closed_pwm = 1890
		self.open_pwm = 1280
		self.twitch=10
		self.release_servo_number = 9 # aux 1
		self.test_servo_numbers = []
		# self.test_servo_numbers = [11,12,13]
		self.release_altitude = self.home['release_alt']
		self.current_test_servo_pwm = self.closed_pwm
		self.released = False
		self.flight_mission_started = False

		self.flight = None

		logging.basicConfig(format='%(asctime)s,%(message)s')
		self.logger = logging.getLogger('mission_log')
		rotatingLog=RotatingFileHandler('mission.log', maxBytes=1000000, backupCount=100)
		rotatingLog.setLevel(logging.DEBUG)
		self.logger.setLevel(logging.DEBUG)
		self.logger.addHandler(rotatingLog)

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

	def logInfo(self, message):
		self.logger.info(logMessage(message))

	def logDebug(self, message):
		self.logger.debug(logMessage(message))

	def logMessage(self, message)
		frame=self.vehicle.location.global_relative_frame
		return "%d,%f,%f,'%s'" % (frame.alt, frame.lat, frame.lng, message)

	# Moves servo 9 (aux 1) to release payload
	def release_payload(self):
		self.logInfo("!!!!!RELEASING PAYLOAD!!!!!")
		start_new_thread(self.set_servo, (self.release_servo_number, self.open_pwm,))
		self.released = True
		if not self.flight_mission_started:
			self.flight_mission_started = True
			start_new_thread(self.start_flight_mission, ())

	# Moves servo 9 (aux 1) to closed to hold payload
	def lock_payload(self):
		self.logInfo("!!!!!LOCKING PAYLOAD!!!!!")
		start_new_thread(self.set_servo, (self.release_servo_number, self.closed_pwm,))
		self.released = False


	# Main mission - should be executed after release
	def start_flight_mission(self):
		self.flight = Flight(self.connection, self.home)
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
			self.logInfo("moving test servos")
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
		self.logInfo(" GPS: %s" % self.connection.gps_0)
		self.logInfo(" Battery: %s" % self.connection.battery)
		self.logInfo(" Last Heartbeat: %s" % self.connection.last_heartbeat)
		self.logInfo(" Is Armable?: %s" % self.connection.is_armable)
		self.logInfo(" System status: %s" % self.connection.system_status.state)
		self.logInfo(" Mode: %s" % self.connection.mode.name)

	def stop(self):
		return os.path.isfile("/home/apsync/stopmission")

	def release_now(self):
		return os.path.isfile("/home/apsync/releasenow")

	def autopilot(self):

		# TODO use GPS Fix = 3D before allowing continue?
		# TODO check if safety switch activated?
		while not self.connection.is_armable and not self.stop():
			self.logInfo( "Initialising...." )
			time.sleep(5)

		self.logInfo("Desired release altitude = %s" % self.release_altitude )

		# Make sure the payload release is in the closed position
		self.lock_payload()

		while not self.stop():
			self.move_test_servos()
			time.sleep(3)

		logging.shutdown()
		self.connection.close()

def start_flight(connection_string):
	drone = Drone(connection_string)
	drone.logInfo("Connecting to plane on %s" % (drone.connection_string,))
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
					drone.logInfo( "gps time %s" % gpstime )
					drone.logInfo( "sys time %s" % systime )
					drone.logInfo( "diff %s" % difftime )
					drone.logInfo("Setting system time to match GPS")
					if sys.platform in ['linux', 'linux2', 'darwin']:
						os.system("sudo date +%s -s @%s" % ('%s', gpstime))
			else:
				drone.logInfo( "The GPS returned time since boot instead of time since epoch so can't use it for system time" )

	@connection.on_attribute('location.global_frame')
	def listener_position(vehicle, name, message):
		alt = message.alt
		rel_alt = alt - drone.home['alt']
		ts = int(time.time()*10)
		if ts % 25 == 0:
			drone.logInfo( "Rel Alt %s" % rel_alt )
		if drone.flight:
			drone.flight.alt = alt
			drone.flight.lng = message.lon
			drone.flight.lat = message.lat	
		if alt >= drone.release_altitude and not drone.released:
			drone.log ( "Releasing payload at %s metres relative to home" % rel_alt)
			drone.release_payload()
		else:
			drone.twitch_release_servo()
		if drone.release_now() and not drone.released:
			drone.log ( "Forced Releasing payload at %s metres relative to home" % rel_alt)
			drone.release_payload()

	drone.report()
	drone.autopilot()

if __name__ == '__main__':
	start_flight('0.0.0.0:9000')

