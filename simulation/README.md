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

# Running the simulator

- ssh into the virtual machine
    - `vagrant ssh`
- `cd ardupilot/ArduPlane`
- Run the simulator:
    - `sim_vehicle.py --console --aircraft test`
- Wait a few seconds for the simulator to initialise then load a sample mission
    - `wp load ../Tools/autotest/ArduPlane-Missions/CMAC-toff-loop.txt`
- Then change arm the motors and start the mission:
    - `arm throttle`
    - `mode auto`
- You will see the mission height and status as it plays through
- Press ^c to leave the simulation at anytime

# TODO
## Visualise the mission on a remote FlightGear
- See the http://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html
- Open UDP 5503 via ssh link so remote flightgear can connect

## Control the mission with the python script (which is the whole point!)
- Start mavproxy as part of the vagrant build and configure the mission script to connect?
- How to lift the plane to simulate a balloon launch?
- How to show change in release servo?
- Script to look for safety switch pressed to start the control loop?
