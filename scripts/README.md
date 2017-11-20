Running the drop test simulation

In a termal window, start a simulated plane and add an extra MAVLink output to localhost port 5769
cd ardupilot/ArduPlane
sim_vehicle.py
MANUAL>output add 127.0.0.:5769


In a new termal, startup the FlightGear simulator with the plane model
cd ardupilot/Tools/autotest/
./fg_plane_view.sh


In yet another terminal run the dronekit script to start the mission:
cd ~/eesa/scripts
python ./simulate_mission.py


TODO
Magically increase GPS altitude to simulate a balloon lift


