# Simulation

Since not everyone on the project has a Pixhawk 2.1 with Intel Edison, this simulation VM should make it easier for us to collaborate.

# Prerequisites

- OSX (Dockerfile will need tweaking for linux)
- Python 2.7 installed
- This repo cloned

# Plane Architecture

![Space Plane Architecture](https://github.com/EqualExperts/eesa/blob/master/simulation/Space%20Plane%20Architecture.png)

# Simulation Architecture

![Simulation Architecture](https://github.com/EqualExperts/eesa/blob/master/simulation/SITL.png)

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
Step 3 (Optional): Start the FlightGear Sim

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

Logs are output to mission.log and flight.log

If you have problems installing the dronekit library, see http://python.dronekit.io/develop/installation.html

## TODO
- Get local flightgear connecting to sitl on docker
- output status to log when Waiting for arm...
- Dockerfile - Stop ardupilot recompile on run
- Magically increase GPS altitude to simulate a balloon lift
- Fix height/altitude in sitl - should not = home
- Overlay for Ardupilot to allow arm and drop from altitude, instead of patch file
- Improve SITL simulation of air pressure decrease with altitude
- runtime configuration to switch from macos to linux without having two images
- unit tests for mission.py and flight.py
    - test release at 30,000m
    - test emeergency actions
        - loss of GPS
        - low battery
        - hardware failure
        - early balloon burst

## Links
- SITL
    - Software in the loop.  Replaces the Pixhawk hardware for testing
    - Summary: http://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html
    - Advanced testing: http://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html
- Running as a daemon (for Docker containers)
    - https://ardupilot.github.io/MAVProxy/html/getting_started/starting.html
- Connecting to the Ardupilot firmware
    - MavLINK protocol: http://ardupilot.org/dev/docs/mavlink-commands.html
    - Python Dronekit (built on MavLINK): http://python.dronekit.io/
- Physics Simulator used in SITL
    - https://github.com/JSBSim-Team/jsbsim

