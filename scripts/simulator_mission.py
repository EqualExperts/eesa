import mission

#Connect to remote SITL instance
connection_string = "udp:127.0.0.1:5769"

mission.start_flight(connection_string)

