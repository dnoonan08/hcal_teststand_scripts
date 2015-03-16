# This module contains functions for talking to the GLIB.

from re import search
from subprocess import Popen, PIPE
import ngccm

# FUNCTIONS:
def get_info(port):		# Returns a dictionary of information about the GLIB, such as the FW version.
	data = {
		"version_fw_d": ['get fec1-user_firmware_dd', 0],
		"version_fw_m": ['get fec1-user_firmware_mm', 0],
		"version_fw_y": ['get fec1-user_firmware_yy', 0],
	}
	log = ""
	raw_output = ngccm.send_commands(port, [data[info][0] for info in data.keys()])["output"]
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
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "glib.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
