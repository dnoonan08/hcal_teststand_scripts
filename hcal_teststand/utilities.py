# IMPORTS:
import sys
from time import time, sleep
from datetime import datetime
# /IMPORTS

# CLASSES:
class logger:		# Using http://stackoverflow.com/a/5916874 as a blueprint
	def __init__(self, f="test.log"):
		self.terminal = sys.stdout
		self.log = open(f, "a")
	
	def write(self, message=""):
		self.terminal.write(message)
		self.log.write(message)
		return message

# /CLASSES

# FUNCTIONS:
def time_string():
	return datetime.now().strftime("%y%m%d_%H%M%S.%f")[:-3]		# Chop off the last three decimal places, leaving three (not rounding).

def time_to_string(t):
	return datetime.fromtimestamp(t).strftime("%y%m%d_%H%M%S.%f")[:-3]

def string_to_time(string):
#	string = string.split(".")[0]		# Ignore possible decimals in seconds.
	pieces = string.split("_")
	time_object = datetime(int(pieces[0][:2]), int(pieces[0][2:4]), int(pieces[0][4:6]), int(pieces[1][:2]), int(pieces[1][2:4]), float(pieces[1][4:]))
	delta = time_object - datetime.utcfromtimestamp(0)
	return delta.total_seconds()

def list_to_string(l=None, n=2):
	if l != None:
		if not isinstance(l, list):
			l = [l]
		try:
			l_str = ["{0:.{1}f}".format(i, n) for i in l]
			return "[" + reduce(lambda x, y: x + ", " + y, l_str) + "]"
		except Exception as ex:
			print ex
			return ""
	else:
		return ""
# /FUNCTIONS
