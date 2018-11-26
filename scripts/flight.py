import time
import sys
import os
import os.path
sys.path.append("/home/apsync/dronekit-python/")
from dronekit import VehicleMode, Command, LocationGlobalRelative, LocationGlobal
from pymavlink import mavutil
import logging
from logging.handlers import RotatingFileHandler

class Flight(object):

	min_release_alt=2000
	max_release_alt=30000
	min_throttle=5
	max_throttle=75
	minimum_calculated_target_speed=15
	maximum_calculated_target_speed=90
	minimum_calculated_min_speed=8
	maximum_calculated_min_speed=80
	minimum_calculated_throttle=5
	maximum_calculated_throttle=50
	minimum_calculated_min_pitch=4500
	maximum_calculated_min_pitch=9000
	minimum_calculated_max_pitch=500
	maximum_calculated_max_pitch=3000

	altitude_step=0.9
	
	def __init__(self, vehicle, home):
		self.vehicle = vehicle
		self.home = home
		frame=self.vehicle.location.global_frame
		self.alt=frame.alt
		self.lat=frame.lat
		self.lng=frame.lon
		
		self.vehicle.parameters['FS_SHORT_ACTN']=3
		self.vehicle.parameters['FS_LONG_ACTN']=0
		self.vehicle.parameters['ARMING_CHECK']=2048
		self.vehicle.parameters['TKOFF_THR_MINACC']=0

		self.vehicle.parameters['LIM_PITCH_MAX']=700 #(i.e. can't climb)
		self.vehicle.parameters['LIM_PITCH_MIN']=-9000 #(straight down)
		self.vehicle.parameters['TRIM_THROTTLE']=5
		self.vehicle.parameters['THR_MAX']=5
		self.vehicle.parameters['STAB_PITCH_DOWN']=15
		self.vehicle.parameters['ARSPD_FBW_MAX']=100 #(max for ardupilot)
		self.vehicle.parameters['ARSPD_FBW_MIN']=90
		self.vehicle.parameters['TRIM_ARSPD_CM']=9500
		self.vehicle.parameters['ARSPD_USE']=0

		logging.basicConfig(format='%(asctime)s,%(message)s')
		self.logger = logging.getLogger('mission_log')
		rotatingLog=RotatingFileHandler('flight.log', maxBytes=1000000, backupCount=100)
		rotatingLog.setLevel(logging.INFO)
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(rotatingLog)


	def takeoff(self):

		self.set_home()

		self.change_mode("MANUAL")
		if self.alt > self.min_release_alt:
			time.sleep(5) # wait for a little speed to build up
		self.load_mission()
	
		self.arm("FBWA")
		self.change_mode("AUTO")
	
		self.logInfo("Delaying to allow takeoff to happen")
		time.sleep(5)

		while self.alt > self.min_release_alt:
			if self.alt < 5000:
				## Only use airspeed sensor when below 5km
				self.vehicle.parameters['ARSPD_USE']=1

			## Calculate graduated target speed, stall speed, throttle and pitch
			mission_percentage=((self.alt-self.min_release_alt)/(self.max_release_alt-self.min_release_alt))*100
			target_speed=int((self.maximum_calculated_target_speed-self.minimum_calculated_target_speed)*(mission_percentage/100))+self.minimum_calculated_target_speed
			max_speed=target_speed+10
			min_speed=int((self.maximum_calculated_min_speed-self.minimum_calculated_min_speed)*(mission_percentage/100))+self.minimum_calculated_min_speed
			min_pitch=int((self.maximum_calculated_min_pitch-self.minimum_calculated_min_pitch)*(mission_percentage/100))+self.minimum_calculated_min_pitch
			throttle=self.maximum_calculated_throttle-int((self.maximum_calculated_throttle-self.minimum_calculated_throttle)*(mission_percentage/100))
			max_pitch=self.maximum_calculated_max_pitch-int((self.maximum_calculated_max_pitch-self.minimum_calculated_max_pitch)*(mission_percentage/100))

			self.logInfo("Alt "+str(self.alt)+"m, "+str(int(mission_percentage))+"%, max_pitch "+str(max_pitch)+", min_pitch "+str(min_pitch))
			self.logInfo("Alt "+str(self.alt)+"m, "+str(int(mission_percentage))+"%, max_speed "+str(max_speed)+"m/s, target "+str(target_speed)+"m/s, min_speed "+str(min_speed)+"m/s")
			self.logInfo("Alt "+str(self.alt)+"m, "+str(int(mission_percentage))+"%, throttle "+str(throttle)+"%")
			self.logInfo("----")

			self.vehicle.parameters['LIM_PITCH_MAX']=max_pitch
			self.vehicle.parameters['LIM_PITCH_MIN']=0-min_pitch
			self.vehicle.parameters['TRIM_THROTTLE']=throttle
			self.vehicle.parameters['THR_MAX']=throttle+10
			self.vehicle.parameters['ARSPD_FBW_MAX']=max_speed
			self.vehicle.parameters['ARSPD_FBW_MIN']=min_speed
			self.vehicle.parameters['TRIM_ARSPD_CM']=target_speed*100
			self.vehicle.flush()
			
			target_alt = self.alt * self.altitude_step
			self.goto_altitude(target_alt)
			## Allow the flight controller to do it's thing for 60 seconds
			count=0
			while count < 60 and self.alt > target_alt:
				count+=1
				time.sleep(1)

		## Last approach to primary landing site
		self.vehicle.parameters['ARSPD_USE']=1
		self.vehicle.parameters['ARSPD_FBW_MAX']=25
		self.vehicle.parameters['ARSPD_FBW_MIN']=10
		self.vehicle.parameters['TRIM_ARSPD_CM']=12
		self.vehicle.parameters['STAB_PITCH_DOWN']=2
		
		self.vehicle.parameters['LIM_PITCH_MAX']=4500 # ???? Whats the default ???
		self.vehicle.parameters['LIM_PITCH_MIN']=-4500 # ???? Whats the default ???
		self.vehicle.parameters['TRIM_THROTTLE']=33
		self.vehicle.parameters['THR_MAX']=75
		
		self.goto_altitude(self.home['alt'])

		## Keep the script alive until landing
		self.logInfo( "alt = "+str(self.alt))
		while True:
			self.logInfo( "Waiting to land, alt = "+str(self.alt))
			time.sleep(300)

		self.logInfo("Landed")

	def change_mode(self, mode_name):
		mode = VehicleMode(mode_name)
		while self.vehicle.mode.name != mode_name:
			self.logInfo("Waiting for "+mode_name+"...")
			self.vehicle.mode = mode
			time.sleep(1)
	
	def load_mission(self):
		lat=self.vehicle.location.global_frame.lat
		lng=self.vehicle.location.global_frame.lon
		take_off_alt=self.alt*1.1
		cmds = self.vehicle.commands
		cmds.clear()
		self.logInfo( "Loading mission with takeoff from %s to %s meters" % (self.alt,take_off_alt) )
		# Repeat first command because of bug in SITL
		cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 45, 0, 0, 0, 0, 0, 100))
		cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 45, 0, 0, 0, 0, 0, 100))
		self.vehicle.flush()

	def goto_altitude(self, target_altitude):
		self.logInfo( "Heading to target altitude %s meters" % (target_altitude) )
		self.change_mode("GUIDED")
		point = LocationGlobal(self.home['lat'], self.home['lng'], target_altitude)
		self.vehicle.simple_goto(point)

	def arm(self, mode):
		self.change_mode(mode)
		self.vehicle.armed=True
		self.vehicle.flush
		while not self.vehicle.armed:
			self.logInfo(" Waiting for arming...")
			time.sleep(1)
			self.vehicle.armed=True

	def set_home(self):
		while not self.vehicle.home_location:
			cmds = self.vehicle.commands
			cmds.download()
			cmds.wait_ready()
			if not self.vehicle.home_location:
				self.logInfo("Waiting for home location ...")
				tims.sleep(1)
		self.logInfo("Old home location: %s" % self.vehicle.home_location)
		self.vehicle.home_location=LocationGlobal(self.home['lat'], self.home['lng'],self.home['alt'])
		while not self.vehicle.home_location:
			cmds = self.vehicle.commands
			cmds.download()
			cmds.wait_ready()
			if not self.vehicle.home_location:
				self.logInfo("Waiting for home location ...")
				tims.sleep(1)
		self.logInfo("NEW home location: %s" % self.vehicle.home_location)

	def logInfo(self, message):
		self.logger.info(self.logMessage(message))

	def logDebug(self, message):
		self.logger.debug(self.logMessage(message))

	def logMessage(self, message):
                if self.vehicle:
			return "%d,%f,%f,'%s'" % (self.alt, self.lat, self.lng, message)
                else:
                        return "-,-,-,'%s'" % message
