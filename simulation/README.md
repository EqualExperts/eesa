# Simulation

Since not everyone on the project has a Pixhawk 2.1 with Intel Edison, this simulation VM should make it easier for us to collaborate.

# Prerequisites

- OSX (Dockerfile will need tweaking for linux)
- Python 2.7 installed
- This repo cloned

# Plane Architecture

![Space Plane Architecture](https://github.com/EqualExperts/eesa/blob/master/simulation/Space%20Plane%20Architecture.png)

# Running the drop test simulation
Step 0: clone eesa
```
git clone git@github.com:EqualExperts/eesa.git
```

Step 1: Build and run the Docker container for SITL and ArduPlane
```
cd eesa/simulation
docker build -t="eesa/simulation" .
docker run --name sim_eesa -d eesa/simulation
docker logs -f sim_eesa
```
Step 3: Start the FlightGear Sim (optional)
In a new termal, startup the FlightGear simulator with the plane model
```
./fg.sh
```
FlightGear version 2017.3.1 is working well for me.  It seems more likely to work if FlightGear is started before the simulated vehicle.

Step 4: Run the companion EESA mission script
In yet another terminal run the dronekit script to start the mission:
```
sudo pip install dronekit
cd ~/eesa/scripts
python mission.py
```

If you have problems installing the dronekit library, see http://python.dronekit.io/develop/installation.html

## TODO
- output status to log when Waiting for arm...
- Dockerfile - Stop ardupilot recompile on run
- Dockerfile - UDP host defaults to Mac address but can be overridden for linux
- Get local flightgear connecting to sitl on docker
- Fix height/altitude in sitl - should not = home
- Does initial altitude = altitude specified in locations.txt?
- Magically increase GPS altitude to simulate a balloon lift
- Overlay for Ardupilot to allow arm and drop from altitude
- Improve SITL simulation of air pressure decrease with altitude

