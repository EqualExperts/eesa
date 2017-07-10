import dronekit_sitl
import mission

sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

mission.start_flight(connection_string)

sitl.stop()