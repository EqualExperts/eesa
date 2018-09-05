import time
import sys
import os
import os.path
sys.path.append("/home/apsync/dronekit-python/")
from dronekit import VehicleMode, Command

class Flight(object):

	home = { 'latitude': 123.456, 'longitude': 567.890, 'altitude': 90 }

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
	minimum_calculated_max_pitch=0
	maximum_calculated_max_pitch=4

	altitude_step=100
	
	def __init__(self, vehicle, alt)
		self.vehicle = vehicle
		self.alt(alt)
		self.set_home()
		self.vehicle.parameters['TKOFF_THR_MINACC']=2
		self.vehicle.parameters['LIM_PITCH_MAX']=0 #(i.e. can't climb)
		self.vehicle.parameters['LIM_PITCH_MIN']=-9000 #(straight down)
		self.vehicle.parameters['TRIM_THROTTLE']=5
		self.vehicle.parameters['THR_MAX']=5
		self.vehicle.parameters['STAB_PITCH_DOWN']=15
		self.vehicle.parameters['ARSPD_FBW_MIN']=100 #(max for ardupilot)
		self.vehicle.parameters['ARSPD_FBW_MIN']=90
		self.vehicle.parameters['TRIM_ARSPD_CM']=9500
		self.vehicle.parameters['ARSPD_USE']=0

	def alt(self,alt)
		self.alt = alt
	
	def takeoff(self):
		self.arm()

		self.alt=self.vehicle.location.global_relative_frame.alt
		if self.alt > min_release_alt 
			time.sleep(5) # wait for a little speed to build up
		self.load_mission()
	
		change_mode("AUTO")
	
		self.log("Delaying to allow takeoff to happen")
		time.sleep(5)
	
		## ????  Use global_rel_frame or inject alt from listener ????
		self.alt=self.vehicle.location.global_relative_frame.alt
		while self.alt > min_release_alt:
			if self.alt < 5000:
				## Only use airspeed sensor when below 5km
				self.vehicle.parameters['ARSPD_USE']=1

			## Calculate graduated target speed, stall speed, throttle and pitch
			mission_percentage=((alt-min_release_alt)/(max_release_alt-min_release_alt))*100
			target_speed=int((maximum_calculated_target_speed-minimum_calculated_target_speed)*(mission_percentage/100))+minimum_calculated_target_speed
			max_speed=target_speed+10
			min_speed=int((maximum_calculated_min_speed-minimum_calculated_min_speed)*(mission_percentage/100))+minimum_calculated_min_speed
			min_pitch=int((maximum_calculated_min_pitch-minimum_calculated_min_pitch)*(mission_percentage/100))+minimum_calculated_min_pitch
			throttle=maximum_calculated_throttle-int((maximum_calculated_throttle-minimum_calculated_throttle)*(mission_percentage/100))
			max_pitch=maximum_calculated_max_pitch-int((maximum_calculated_max_pitch-minimum_calculated_max_pitch)*(mission_percentage/100))
			## TODO Use logger class ????
			self.log ("Alt "+str(alt)+"m, "+str(int(mission_percentage))+"%, max_pitch "+str(max_pitch)+"m/s, min_pitch "+str(min_pitch))
			self.log ("Alt "+str(alt)+"m, "+str(int(mission_percentage))+"%, max_speed "+str(max_speed)+"m/s, target "+str(target_speed)+"m/s, min_speed "+str(min_speed)+"m/s")
			self.log ("Alt "+str(alt)+"m, "+str(int(mission_percentage))+"%, throttle "+str(throttle)+"%")
			self.log ("----")

			self.vehicle.parameters['LIM_PITCH_MAX']=max_pitch
			self.vehicle.parameters['LIM_PITCH_MIN']=0-min_pitch
			self.vehicle.parameters['TRIM_THROTTLE']=throttle
			self.vehicle.parameters['THR_MAX']=throttle+10
			self.vehicle.parameters['ARSPD_FBW_MAX']=max_speed
			self.vehicle.parameters['ARSPD_FBW_MIN']=min_speed
			self.vehicle.parameters['TRIM_ARSPD_CM']=target_speed*100
			goto_altitude(self.alt - self.altitude_step)
			## Allow the flight controller to do it's thing for 60 seconds
			time.sleep(60)
			alt=self.vehicle.location.global_relative_frame.alt
	
		## Last approach to primary landing site
		self.vehicle.parameters['ARSPD_USE']=1
		self.vehicle.parameters['ARSPD_FBW_MAX']=25
		self.vehicle.parameters['ARSPD_FBW_MIN']=10
		self.vehicle.parameters['TRIM_ARSPD_CM']=12
		self.vehicle.parameters['STAB_PITCH_DOWN']=2
		
		self.vehicle.parameters['LIM_PITCH_MAX']=4 # ???? Whats the default ???
		self.vehicle.parameters['LIM_PITCH_MIN']=-4500 # ???? Whats the default ???
		self.vehicle.parameters['TRIM_THROTTLE']=33
		self.vehicle.parameters['THR_MAX']=75
		
		self.change_mode("RTL")

		## Keep the script alive until landing
		while alt > 0:
			time.sleep(300)

		self.log ("Landed")

	def change_mode(self, mode_name):
		mode = VehicleMode(mode_name)
		while self.vehicle.mode.name != mode_name:
			self.log("Waiting for "+mode_name+"...")
			self.vehicle.mode = mode
			time.sleep(1)
	
	def set_home(self)
		while not vehicle.home_location:
			cmds = vehicle.commands
			cmds.download()
			cmds.wait_ready()
			if not vehicle.home_location:
				self.log " Waiting for home location ..."
				time.sleep(1)
		self.log("Old home location: %s" % vehicle.home_location)

		vehicle.home_location=LocationGlobal(self.home.latitude, self.home.longitude, self.home.altitude)

	def load_mission(self):
		self.alt=self.vehicle.location.global_relative_frame.alt
		take_off_alt=100
		if self.alt > 100:
			tak_off_alt=0
		cmds = self.vehicle.commands
		cmds.clear()
		cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, take_off_alt))
		self.vehicle.flush()

	def goto_altitude(self, target_altitude):
		change_mode("GUIDED")
		point = LocationGlobal(self.home.latitude, self.home.longitude, target_altitude)
		vehicle.simple_goto(point)

	def arm(self):
		change_mode("FBWA")
		self.vehicle.armed=True
	    while not vehicle.armed:
	        self.log(" Waiting for arming...")
	        time.sleep(1)

	def log(self, message)
		print ( message )
