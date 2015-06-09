from time import time, sleep
from datetime import datetime

def time_string():
	return datetime.now().strftime("%y%m%d.%H%M%S.%f")[:-3]		# Chop off the last four decimal places, leaving two (not rounding).

def time_to_string(t):
	return datetime.fromtimestamp(t).strftime("%y%m%d.%H%M%S.%f")[:-3]
