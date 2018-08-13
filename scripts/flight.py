import time

class Flight(object):

	min_alt=2000
	max_alt=30000
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

	def __init__(self, vehicle, alt)
		self.vehicle = vehicle
		self.alt = alt
		self.set_home(??????)
		self.vehicle.parameters['TKOFF_THR_MINACC']=2
		self.vehicle.parameters['LIM_PITCH_MAX']=0 #(i.e. can't climb)
		self.vehicle.parameters['LIM_PITCH_MIN']=9000 #(straight down)
		self.vehicle.parameters['TRIM_THROTTLE']=5 ???? Max throttle ????
		self.vehicle.parameters['STAB_PITCH_DOWN']=15
		self.vehicle.parameters['ARSPD_FBW_MIN']=100 #(max for ardupilot)
		self.vehicle.parameters['ARSPD_FBW_MIN']=90
		self.vehicle.parameters['TRIM_ARSPD_CM']=9500
		self.vehicle.parameters['THR_MAX']=5
		self.vehicle.parameters['ARSPD_USE']=0

	def alt(self,alt)
		self.alt = alt
	
	def takeoff(self,vehicle):
		self.alt=self.vehicle.location.global_relative_frame
		if alt > 10000m 
			wait 10 seconds
			Load mission (take-off [to current altitude-500] + rtl)
		else
			Load mission (take-off [to current altitude+20] + rtl)
	
		self.vehicle.armed = True
		time.sleep(1)

		change_mode("AUTO")
	
		self.log("Delaying to allow takeoff to happen")
		time.sleep(5)
	
		change_mode("GUIDED")
		
		## ????  Use global_rel_frame or inject alt from listener ????
		alt=self.vehicle.location.global_relative_frame
		while self.alt > 2000:
			if alt > 5000:
				self.vehicle.parameters['ARSPD_USE']=1

			## Calculate graduated target speed, stall speed, throttle and pitch
			mission_percentage=((alt-min_alt)/(max_alt-min_alt))*100
			target_speed=int((maximum_calculated_target_speed-minimum_calculated_target_speed)*(mission_percentage/100))+minimum_calculated_target_speed
			max_speed=target_speed+10
			min_speed=int((maximum_calculated_min_speed-minimum_calculated_min_speed)*(mission_percentage/100))+minimum_calculated_min_speed
			min_pitch=int((maximum_calculated_min_pitch-minimum_calculated_min_pitch)*(mission_percentage/100))+minimum_calculated_min_pitch
			throttle=maximum_calculated_throttle-int((maximum_calculated_throttle-minimum_calculated_throttle)*(mission_percentage/100))
			max_pitch=maximum_calculated_max_pitch-int((maximum_calculated_max_pitch-minimum_calculated_max_pitch)*(mission_percentage/100))
			print ("Alt "+str(alt)+"m, "+str(int(mission_percentage))+"%, max_pitch "+str(max_pitch)+"m/s, min_pitch "+str(min_pitch))
			print ("Alt "+str(alt)+"m, "+str(int(mission_percentage))+"%, max_speed "+str(max_speed)+"m/s, target "+str(target_speed)+"m/s, min_speed "+str(min_speed)+"m/s")
			print ("Alt "+str(alt)+"m, "+str(int(mission_percentage))+"%, throttle "+str(throttle)+"%")
			print ("----")

			self.vehicle.parameters['LIM_PITCH_MAX'] = max_pitch
			self.vehicle.parameters['LIM_PITCH_MIN'] = min_pitch
			self.vehicle.parameters['TRIM_THROTTLE']=throttle # ???? Max throttle ????
			self.vehicle.parameters['THR_MAX']=throttle+10 # ???? Max throttle ????
			self.vehicle.parameters['ARSPD_FBW_MAX']=max_speed
			self.vehicle.parameters['ARSPD_FBW_MIN']=min_speed
			self.vehicle.parameters['TRIM_ARSPD_CM']=target_speed*100
			goto home lat/long with altitude = (current - 100)
			time.sleep(60)
			alt=self.vehicle.location.global_relative_frame
	
		## Last approach to primary landing site
		self.vehicle.parameters['ARSPD_USE']=1
		self.vehicle.parameters['ARSPD_FBW_MAX']=25
		self.vehicle.parameters['ARSPD_FBW_MIN']=10
		self.vehicle.parameters['TRIM_ARSPD_CM']=12
		self.vehicle.parameters['STAB_PITCH_DOWN']=2
		
		self.vehicle.parameters['LIM_PITCH_MAX']=4 # ???? Whats the default ???
		self.vehicle.parameters['LIM_PITCH_MIN']=4500 # ???? Whats the default ???
		self.vehicle.parameters['TRIM_THROTTLE']=33 # ???? Max throttle ????
		self.vehicle.parameters['THR_MAX']=75 # ???? Max throttle ????
		
		self.change_mode("RTL")

		while alt > 0:
			time.sleep(30)

	def change_mode(self, mode_name):
		mode = VehicleMode(mode_name)
		while self.vehicle.mode.name != mode_name:
			self.log("Waiting for "+mode_name+"...")
			self.vehicle.mode = mode
			time.sleep(1)
	
	def set_home(self,latitude, longitude, altitude):
		while not vehicle.home_location:
			cmds = vehicle.commands
			cmds.download()
			cmds.wait_ready()
			if not vehicle.home_location:
				print " Waiting for home location ..."
				time.sleep(1)
		print "Old home location: %s" % vehicle.home_location

		vehicle.home_location=LocationGlobal(latitude,longitude,altitude)

	def launch(self):
		cmds = self.vehicle.commands
		cmds.clear()
		cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 0))
