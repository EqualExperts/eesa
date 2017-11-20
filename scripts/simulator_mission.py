#import dronekit_sitl
import mission

#sitl = dronekit_sitl.start_default()
#connection_string = sitl.connection_string()

#Connect to remote SITL instance
connection_string = "udp:127.0.0.1:5769"

mission.start_flight(connection_string)

#sitl.stop()
