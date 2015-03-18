# This module contains functions for talking to the QIE card.

from re import search
from subprocess import Popen, PIPE
import ngccm

# FUNCTIONS:
def get_bridge_info(port, crate, slot):		# Returns a dictionary of information about the Bridge FPGA, such as the FW versions.
	data = {
		"version_fw_major": ['get HF{0}-{1}-B_FIRMVERSION_MAJOR'.format(crate, slot), 0],
		"version_fw_minor": ['get HF{0}-{1}-B_FIRMVERSION_MINOR'.format(crate, slot), 0],
		"version_fw_svn": ['get HF{0}-{1}-B_FIRMVERSION_SVN'.format(crate, slot), 0],
	}
	log = ""
	raw_output = ngccm.send_commands(port, [data[info][0] for info in data.keys()])["output"]
	for info in data.keys():
		match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)
		if match:
			data[info][1] = int(match.group(1), 16)
		else:
			log += '>> ERROR: Failed to find the result of "{0}". The data string follows:\n'.format(data[info][0])
			match = search("\n({0}.*)\n".format(data[info][0]), raw_output)
			if match:
				log += '{0}\n'.format(match.group(0).strip())
			else:
				log += "Empty\n"
				log += "{0}\n".format(raw_output)
	version_fw = "{0:02d}.{1:02d}.{2:04d}".format(data["version_fw_major"][1], data["version_fw_minor"][1], data["version_fw_svn"][1])
	return {
		"slot":	slot,
		"version_fw_major":	data["version_fw_major"][1],
		"version_fw_minor":	data["version_fw_minor"][1],
		"version_fw_svn":	data["version_fw_svn"][1],
		"version_fw":	version_fw,
		"log":			log.strip(),
	}

def get_igloo_info(port, crate, slot):		# Returns a dictionary of information about the IGLOO2, such as the FW versions.
	data = {
		"version_fw_major_top": ['get HF{0}-{1}-iTop_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		"version_fw_minor_top": ['get HF{0}-{1}-iTop_FPGA_MINOR_VERSION'.format(crate, slot), 0],
		"version_fw_major_bot": ['get HF{0}-{1}-iBot_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		"version_fw_minor_bot": ['get HF{0}-{1}-iBot_FPGA_MINOR_VERSION'.format(crate, slot), 0],
	}
	log = ""
	raw_output = ngccm.send_commands(port, [data[info][0] for info in data.keys()])["output"]
	for info in data.keys():
		match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)
		if match:
			data[info][1] = int(match.group(1), 16)
		else:
			log += '>> ERROR: Failed to find the result of "{0}". The data string follows:\n'.format(data[info][0])
			match = search("\n({0}.*)\n".format(data[info][0]), raw_output)
			if match:
				log += '{0}\n'.format(match.group(0).strip())
			else:
				log += "Empty\n"
				log += "{0}\n".format(raw_output)
	version_fw_top = "{0:02d}.{1:02d}".format(data["version_fw_major_top"][1], data["version_fw_minor_top"][1])
	version_fw_bot = "{0:02d}.{1:02d}".format(data["version_fw_major_bot"][1], data["version_fw_minor_bot"][1])
	return {
		"slot": slot,
		"version_fw_major_top":	data["version_fw_major_top"][1],
		"version_fw_minor_top":	data["version_fw_minor_top"][1],
		"version_fw_top":	version_fw_top,
		"version_fw_major_bot":	data["version_fw_major_bot"][1],
		"version_fw_minor_bot":	data["version_fw_minor_bot"][1],
		"version_fw_bot":	version_fw_bot,
		"log":			log.strip(),
	}

def get_info(port, crate, slot):
	return{
		"bridge": get_bridge_info(port, crate, slot),
		"igloo": get_igloo_info(port, crate, slot),
	}

def get_status(ts):		# Perform basic checks of the QIE cards:
	status = {}
	status["status"] = []
	# Check Bridge FPGA and IGLOO2 version are accessible:
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			qie_info = get_info(ts.ngccm_port, crate, slot)
			if (qie_info["bridge"]["version_fw"] != "00.00.0000"):
				status["status"].append(1)
			else:
				status["status"].append(0)
			if (qie_info["igloo"]["version_fw_top"] != "00.00"):
				status["status"].append(1)
			else:
				status["status"].append(0)
			if (qie_info["igloo"]["version_fw_bot"] != "00.00"):
				status["status"].append(1)
			else:
				status["status"].append(0)
	return status

def set_ped(port, crate, slot, i, n):		# Set the pedestal of QIE i to DAC value n.
	assert isinstance(n, int)
	if abs(n) > 31:
		print ">> ERROR: You must enter a decimal integer between -31 and 31. The pedestals have not been changed."
	else:
		if n <= 0:
			n = abs(n)
		else:
			n = n + 32
		n_str = "{0:#04x}".format(n)		# The "#" prints the "0x". The number of digits to pad with 0s must include these "0x", hence "4" instead of "2".
		commands = ["put HF{0}-{1}-QIE{2}_PedestalDAC {3}".format(crate, slot, i, n_str)]
		raw_output = ngccm.send_commands(port, commands)["output"]
		# Maybe I should include something here to make sure the command didn't return an error? Return 1 if not...

def set_ped_all(port, slot, n):		# n is the decimal representation of the pedestal register.
	# This function is faster than running "set_ped" 24 times.
	assert isinstance(n, int)
	if abs(n) > 31:
		print ">> ERROR: You must enter a decimal integer between -31 and 31. The pedestals have not been changed."
	else:
		if n <= 0:
			n = abs(n)
		else:
			n = n + 32
		n_str = "{0:#04x}".format(n)		# The "#" prints the "0x". The number of digits to pad with 0s must include these "0x", hence "4" instead of "2".
		commands = ["put HF{0}-{1}-QIE{2}_PedestalDAC {3}".format(crate, slot, i+1, n_str) for i in range(24)]
		raw_output = ngccm.send_commands_fast(port, commands)["output"]
		# I should include something here to make sure the command didn't return an error? Return 1 if not...
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "qie.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
