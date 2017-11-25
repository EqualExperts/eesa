# Simulation

Since not everyone on the project has a Pixhawk 2.1 with Intel Edison, this simulation VM should make it easier for us to collaborate.

#  Installation

- Install
    - VirtualBox
    - Vagrant
    - Vagrant Manager
- Create the `vagrant` directory
- cd to the `vagrant` dir
- git clone `https://github.com/dronekit/dronekit-python`
- Download the Vagrantfile from this repo into the `vagrant` dir
- Run `vagrant up`

# Running the drop test simulation

This will run on the vagrant instance detailed above but if you want to visualise the plane using FlightGear, you will need a machine running a desktop/GUI environment.

Based on the instructions for setting up SITL on Linix: http://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html Follow the Install Steps to install dronekit and FlightGear on that page before you run the instructions below.

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


