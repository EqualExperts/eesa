import time

def set_initial_parameters(vehicle):
    Set home = scout centre field (or just over the water next to field?)
    vehicle.parameters['TKOFF_THR_MINACC']=2
    vehicle.parameters['LIM_PITCH_MAX']=0 #(i.e. can't climb)
    vehicle.parameters['LIM_PITCH_MIN']=9000 #(straight down)
    vehicle.parameters['TRIM_THROTTLE']=5
    vehicle.parameters['STAB_PITCH_DOWN']=15
    vehicle.parameters['ARSPD_FBW_MIN']=100 #(max for ardupilot)
    vehicle.parameters['ARSPD_FBW_MIN']=90
    vehicle.parameters['TRIM_ARSPD_CM']=9500
    vehicle.parameters['THR_MAX']=5
    vehicle.parameters['ARSPD_USE']=0

def wait_for_altitude(vehicle):
    while alt < 30000
        wait 10 seconds
    Release servo

def takeoff(vehicle):
    if alt > 10000m 
        wait 10 seconds
        Load mission (take-off [to current altitude-500] + rtl)
    else
        Load mission (take-off [to current altitude+20] + rtl)

    vehicle.armed   = True
    while vehicle.mode.name != "AUTO":
        self.log("Waiting for AUTO...")
        vehicle.mode = VehicleMode("AUTO")
        time.sleep(1)

    self.log("Delaying to allow takeoff to happen")
    time.sleep(15)

    while vehicle.mode.name != "GUIDED":
        self.log("Waiting for GUIDED...")
        vehicle.mode = VehicleMode("GUIDED")
        time.sleep(1)
    
    while alt > 20000m
        vehicle.parameters['LIM_PITCH_MAX']=0
        vehicle.parameters['LIM_PITCH_MIN']=9000 #(straight down)
        vehicle.parameters['TRIM_THROTTLE']=5
        alt=vehicle.location.global_relative_frame
        max_speed=int(50+((alt-20000)*0.005))
        vehicle.parameters['ARSPD_FBW_MAX']=max_speed
        vehicle.parameters['ARSPD_FBW_MIN']=(max_speed-20)
        vehicle.parameters['TRIM_ARSPD_CM']=(max_speed-30)*100
        goto home lat/long with altitude = (current - 1000)
        time.sleep(60)
    
    while alt > 10000m
        vehicle.parameters['ARSPD_USE']=1
        vehicle.parameters['LIM_PITCH_MAX'] = 0
        vehicle.parameters['LIM_PITCH_MIN'] = 7500 
        vehicle.parameters['TRIM_THROTTLE']=15
        max_speed=int(30+((alt-10000)*0.002))
        vehicle.parameters['ARSPD_FBW_MAX']=max_speed
        vehicle.parameters['ARSPD_FBW_MIN']=(max_speed-15)
        vehicle.parameters['TRIM_ARSPD_CM']=(max_speed-20)*100
        goto home lat/long with altitude = (current - 500)
        time.sleep(60)
    
    while alt > 2000m
        vehicle.parameters['ARSPD_USE']=1
        vehicle.parameters['LIM_PITCH_MAX'] = 0
        vehicle.parameters['LIM_PITCH_MIN'] = 4500
        vehicle.parameters['TRIM_THROTTLE']=50
        max_speed=int(25+((alt-2000)*0.001)
        vehicle.parameters['ARSPD_FBW_MAX']=max_speed
        vehicle.parameters['ARSPD_FBW_MIN']=(max_speed-15)
        vehicle.parameters['TRIM_ARSPD_CM']=(max_speed-20)*100
        goto home lat/long with altitude = (current - 100)
        time.sleep(60)

    vehicle.parameters['ARSPD_USE']=1
    vehicle.parameters['ARSPD_FBW_MAX']=25
    vehicle.parameters['ARSPD_FBW_MIN']=10
    vehicle.parameters['TRIM_ARSPD_CM']=12
    vehicle.parameters['STAB_PITCH_DOWN']=2
    
    vehicle.parameters['LIM_PITCH_MAX']=4
    vehicle.parameters['LIM_PITCH_MIN']=4500
    vehicle.parameters['TRIM_THROTTLE']=50
    
    while vehicle.mode.name != "RTL":
        self.log("Waiting for RTL...")
        vehicle.mode = VehicleMode("RTL")
        time.sleep(1)

    while alt > 0:
        time.sleep(30)
