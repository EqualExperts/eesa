# Equal Experts Space Agency

Scripts and documents for the Equal Experts Space Plane

The [Space Plane](https://equalexperts.com/eesa) is a joint project with Addingham Scout Group and Equal Experts.

This project is to detail the tech behind the Space Plane and allow people to contribute.

## Project Goal

Use a weather balloon to lift a fixed-wing UAV to 30km and have it autonomously fly back to the ground.

## Tech overview

The flight computer is a Pixhawk 2.1 with embedded Intel Edison.

The Edison runs Ubuntu linux.  [Dronekit](http://dronekit.io/) python scripts communicate via MAVLink to control the Pixhawk 2.1 flight computer.

The two UAV planes under test are the Buffalo FX-79 with custom inverted V tail and a 2m clone of the Shadow 200 drone.

## Initial script requirements

### Low level drop tests

A heavy lift quadcopter will lift the plane.  At script must detect when the altitude is > 100m and move a servo to release the plane.  The plane must enter stabilize mode, recover horizontal flight and return to land.

We will start with a light toy glider and move to the full size space plane as we gain confidence in the release mechanism.

See the /scripts/drop.py

### High altitude drop

The space plane will be lifted under a weather balloon to 30km.  The python script will move the servo when the desired altitude is reached and the plane will drop.  

The python script will feed instructions to the Pixhawk to override/augment the usual instructions.

- Pixhawk tries to fly the plane at a set airspeed but 
* the speedsensor will not work at very low pressures 
* the GPS will not be very accurate (~100m) so GPS speed will be inaccurate
* to get lift at low pressures, the plane will have to be moving very fast to achieve the airflow over the control and lift surfaces.  The speed at different pressures will vary so will have to be adjusted by the script
- The plane should try to fly horizontally 
* stall detection will be difficult
* very little control at low pressures

See scripts/mission.py



