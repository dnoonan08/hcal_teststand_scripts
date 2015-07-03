# This module contains functions for talking to the GLIB.

from re import search
from subprocess import Popen, PIPE
import ngccm
from time import time, sleep
from numpy import mean, std

# FUNCTIONS:
def get_info(ts):		# Returns a dictionary of information about the GLIB, such as the FW version.
	data = {
		"version_fw_d": ['get fec1-user_firmware_dd', 0],
		"version_fw_m": ['get fec1-user_firmware_mm', 0],
		"version_fw_y": ['get fec1-user_firmware_yy', 0],
	}
	log = ""
	raw_output = ngccm.send_commands(ts, [data[info][0] for info in data.keys()])["output"]
	for info in data.keys():
		match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)
		if match:
			data[info][1] = int(match.group(1), 16)
		else:
			log += '>> ERROR: Failed to find FW versions.\n'
	version_fw = "{0:02d}{1:02d}{2:02d}".format(data["version_fw_y"][1], data["version_fw_m"][1], data["version_fw_d"][1])
	return {
		"version_fw_d":	data["version_fw_d"][1],
		"version_fw_m":	data["version_fw_m"][1],
		"version_fw_y":	data["version_fw_y"][1],
		"version_fw":	version_fw,
		"log":			log.strip(),
	}

def get_status(ts):		# Perform basic checks of the GLIB with the ngccm tool.
	log = ""
	status = {}
	status["status"] = []
	# Ping GLIB:
	ping_result = Popen(["ping -c 1 {0}".format(ts.glib_ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
	if ping_result:
		status["status"].append(1)
	else:
		status["status"].append(0)
	# Check that the version was accessible:
	glib_info = get_info(ts)
	if (int(glib_info["version_fw"]) != 0):
		status["status"].append(1)
	else:
		status["status"].append(0)
	# Check the control (1) and clock (2):
	ngccm_output = ngccm.send_commands(ts, ["get fec1-ctrl", "get fec1-user_wb_regs"])["output"]
	log += ngccm_output
	## (1) check control data:
	match = search("{0} # ((0x)?[0-9a-f]+)".format("get fec1-ctrl"), ngccm_output)
	if match:
		value = int(match.group(1), 16)
		if (value == int("0x10aa3071", 16)):
			status["status"].append(1)
		else:
			log += "ERROR: The result of {0} was {1}, not {2}".format("get fec1-ctrl", value, int("0x10aa3071", 16))
			status["status"].append(0)
	else:
		log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get fec1-ctrl")
		status["status"].append(0)
	## (2) check the 40 MHz clock:
	match = search("{0} # '(.*)'".format("get fec1-user_wb_regs"), ngccm_output)
	if match:
		values = match.group(1).split()
		clock = float(int(values[-5], 16))/10000
		status["clock"] = clock
		if ( (clock > 40.0640) and (clock < 40.0895) ):
			status["status"].append(1)
		else:
			log += "ERROR: The clock frequency of {0} MHz is not between {1} and {2}.".format(clock, 40.0640, 40.0895)
			status["status"].append(0)
	else:
		log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get fec1-user_wb_regs")
		status["status"].append(0)
	# Check QIE resets:
	f_orbit = get_frequency_orbit(ts)
	if (f_orbit["f"] < 13000 and f_orbit["f"] > 10000 and f_orbit["f_e"] < 500):
		status["status"].append(1)
	else:
		status["status"].append(0)
	status["orbit"] = [f_orbit["f"], f_orbit["f_e"]]
	return status

def read_counter_qie(ts):
	count = -1
	cmd = "get fec1-qie_reset_cnt"
	raw_output = ngccm.send_commands(ts, cmd)["output"]
	match = search(cmd + " # ((0x)?[0-9a-f]+)", raw_output)
	if match:
		count = int(match.group(1),16)
#	else:
#		print "ERROR:"
	return count

def get_frequency_orbit(ts):
	c = []
	t = []
	for i in range(6):
		c.append(read_counter_qie(ts))
		t.append(time())
		sleep(0.01)
	f = []
	for i in range(len(c)-1):
		f.append((c[i+1]-c[i])/(t[i+1]-t[i]))
	return{
		"f_list":	f,
		"f":	mean(f),
		"f_e":	std(f)/(len(f)**0.5),
	}
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "glib.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
