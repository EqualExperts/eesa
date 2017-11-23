# Running the drop test simulation

In a new termal, startup the FlightGear simulator with the plane model
```
cd ardupilot/Tools/autotest/
./fg_plane_view.sh
```
FlightGear version 2017.3.1 is working well for me.  It seems more likely to work if FlightGear is started before the simulated vehicle.

In another termal window, start a simulated plane and add an extra MAVLink output to localhost port 5769
```
cd ardupilot/ArduPlane
sim_vehicle.py --out 127.0.0.:5769 -j4
```
If you see a black FlightGear screen, you may need to switch the  Environment->Time->Midday 

In yet another terminal run the dronekit script to start the mission:
```
cd ~/eesa/scripts
python ./simulate_mission.py
```

Back in the `sim_vehicle.py` terminal, there should be a `MANUAL>` prompt.  If not, press enter to show it.  The `simulate_mission.py` will now be waiting for an altitude of 654m.  I've not found a way to increase altitude without flying a mission, so a mission it is - at the `MANUAL>` prompt, enter the following:

```
wp load ../Tools/autotest/ArduPlane-Missions/CMAC-toff-loop.txt
arm throttle
mode auto
```

You should see the plane takeoff and climb.  Once it's reached 684m, the `mission.py` script will change the mode and fly it back to the start.

## TODO
- Magically increase GPS altitude to simulate a balloon lift
- Move the simulation scripts to ../simulation but still import mission.py
- Make a `simulate_lift.py` script
- `simulate_mission.py` should inject a relative altitude + 100m


