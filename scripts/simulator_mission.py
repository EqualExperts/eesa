from dronekit_sitl import SITL
import mission

args = ['--model', 'plane',]

sitl = SITL() # load a binary path (optional)
sitl.download("plane", "3.3.0", verbose=False)
sitl.launch(args, verbose=False, await_ready=Falses, restart=False)
sitl.block_until_ready(verbose=False)

mission.start_flight(sitl.connection_string())

code = sitl.complete(verbose=False)
sitl.poll()
sitl.stop()
