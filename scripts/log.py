import time
import logging
from logging.handlers import RotatingFileHandler


class FlightLog(object):

	def __init__(self, filename):
		self.logger = logging.getLogger(filename)
		rotatingLog=RotatingFileHandler('flight.log', maxBytes=1000000, backupCount=100)
		rotatingLog.setLevel(logging.INFO)
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(rotatingLog)

	def logInfo(self, vehicle, message):
		self.logger.info(self.logMessage(vehicle, message))

	def logDebug(self, vehicle, message):
		self.logger.debug(self.logMessage(vehicle, message))

	def logMessage(self, vehicle, message):
		thetime = time.asctime(time.localtime())
		if vehicle:
			frame = vehicle.location.global_frame
			return "%s,%d,%f,%f,'%s'" % (thetime,frame.alt, frame.lat, frame.lon, message)
		else:
			return "%s,-,-,-,'%s'" % (thetime,message)

	def report(self, vehicle):
		self.logInfo(vehicle, " GPS: %s" % vehicle.gps_0)
		self.logInfo(vehicle, " Battery: %s" % vehicle.battery)
		self.logInfo(vehicle, " Last Heartbeat: %s" % vehicle.last_heartbeat)
		self.logInfo(vehicle, " Is Armable?: %s" % vehicle.is_armable)
		self.logInfo(vehicle, " System status: %s" % vehicle.system_status.state)
		self.logInfo(vehicle, " Mode: %s" % vehicle.mode.name)
