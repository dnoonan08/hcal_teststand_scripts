####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: This module contains functions for talking to the   #
# FC7s.                                                            #
####################################################################

from re import search
from subprocess import Popen, PIPE
import ngfec
from time import time, sleep
from numpy import mean, std

# CLASSES:
class fc7:
	# Construction:
	def __init__(self, ts=None, crate=None, slot=None, ips=[], n=1):
		self.ts = ts
		self.end = "be"
		self.crate = crate
		self.slot = slot
		if not ips:
			ips = []
		self.ips = ips
		self.n = n
	
	# String behavior
	def __str__(self):
		try:
			return "<FC7 in BE Crate {0}, BE Slot {1}: IPs = {2}>".format(self.crate, self.slot, self.ips)
		except Exception as ex:
#			print ex
			return "<empty fc7 object>"
	
	# Methods:
	def update(self):
		info = get_info(ts=self.ts, n=self.n)
		for key, value in info.iteritems():
			setattr(self, key, value)
		return True
	
	def Print(self):
		print self
	
#	def setup(self):
#		return setup(ip=self.ip, control_hub=self.control_hub)
	# /Methods
# /CLASSES

# FUNCTIONS:
def get_info(ts=None, n=1):		# Returns a dictionary of information about the FC7, such as the FW version.
	# Variables and arguments:
	data = {
		'get fec{0}-firmware_ver_build'.format(n): ["fw_build", -1],
		'get fec{0}-firmware_ver_major'.format(n): ["fw_major", -1],
		'get fec{0}-firmware_ver_minor'.format(n): ["fw_minor", -1],
		'get fec{0}-firmware_yy'.format(n): ["fw_yy", -1],
		'get fec{0}-firmware_mm'.format(n): ["fw_mm", -1],
		'get fec{0}-firmware_dd'.format(n): ["fw_dd", -1],
	}
	
	# Ask the board for information:
	output = ngfec.send_commands(ts=ts, cmds=data.keys())
	
	# Analyze the output:
	for cmd in data.keys():
#		print cmd
		result = [i["result"] for i in output if i["cmd"] == cmd][0]
#		print result
		if "ERROR" not in result:
			value = int(result, 16)
			data[cmd][1] = value
		else:
			print "ERROR (fc7.get_info): Could not fetch the required information:"
			print "\t{0} -> {1}".format(cmd, result)
	
	# Organize and return the information:
	out = {}
	for key, values in data.iteritems():
		out[values[0]] = values[1]
	out["fw"] = [(out["fw_build"], out["fw_major"], out["fw_minor"]), (out["fw_yy"], out["fw_mm"], out["fw_dd"])]
	return out
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "fc7.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
