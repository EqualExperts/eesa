# Simulation

Since not everyone on the project has a Pixhawk 2.1 with Intel Edison, this simulation VM should make it easier for us to collaborate.

#  Prerequisites

- Linux (tested on Ubuntu 16.04 and 18.04)
- Python 2.7 installed

# Running the drop test simulation


Step 1: Install ardupilot and the simulator
Based on the instructions for setting up SITL on Linix: http://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html Follow the Install Steps to install FlightGear on that page before you run the instructions below.

Step 2: Install dronekit
- git clone `https://github.com/dronekit/dronekit-python`

Step 3: Start the FlightGear Sim (optional)
In a new termal, startup the FlightGear simulator with the plane model
```
cd ardupilot/Tools/autotest/
./fg_plane_view.sh
```
FlightGear version 2017.3.1 is working well for me.  It seems more likely to work if FlightGear is started before the simulated vehicle.

Step 4: Edit locations and add Iceland
Edit ardupilot/ArduPlane/Tools/autotest/locations.txt
Add
```
ICEL=64.073,-19.754,10000,180
```

Step 5: Start the ArduPlane SITL Simulator
- todo edit takeoff tool to allow drop from altitude
In another termal window, start a simulated plane and add an extra MAVLink output to localhost port 5769
```
cd ardupilot/ArduPlane
rm -f mav.* eeprom.bin && ../../ardupilot/Tools/autotest/sim_plane.py --out 127.0.0.1:9000 --console -L ICEL
```
The rm command ensures that arduplane will be rebuild and a new simulator firmware used.  This is so the latest changes in the ardupilot C code are run.

If you see a black FlightGear screen, you may need to switch the  Environment->Time->Midday 

Step 6: Run the companion EESA mission script
In yet another terminal run the dronekit script to start the mission:
```
sudo pip install dronekit
git clone git@github.com:EqualExperts/eesa.git
cd ~/eesa/scripts
python mission.py
```

If you have problems installing the dronekit library, see http://python.dronekit.io/develop/installation.html

## TODO
- Magically increase GPS altitude to simulate a balloon lift
- Overlay for Ardupilot to allow arm and drop from altitude
- Improve SITL simulation of air pressure decrease with altitude
- Create Docker image (without flightgear)

