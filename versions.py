from re import search
from subprocess import Popen, PIPE

def get_amc_info():
	raw_output = Popen(['printf "fv\nq" | AMC13Tool2.exe -c ~elaird/AMC13_sn54.xml'], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
#	print raw_output[0]
#	print raw_output[1]
	version_sw = 0
	version_fw = []
	sn = -1
	log = '=== STDOUT ===\n{0}\n\n=== STDERR ===\n{1}\n\n=== Parsing Errors ===\n'.format(raw_output[0].strip(), raw_output[1].strip())
	try:
		match = search("Using AMC13 software ver:\s*(\d+)", raw_output[1])		# For some reason the software verion number is printed on stderr...
		version_sw = int(match.group(1))
	except Exception as ex:
		log += "Trying to find AMC13 software version number resulted in: {0}\n".format(ex)
	try:
		match = search("SN:\s+(\d+)\s+T1v:\s+(\d+)\s+T2v:\s+(\d+)", raw_output[0].strip())		# Look in stdout for the firmware version.
		sn = int(match.group(1))
		version_fw.append(int(match.group(2)))
		version_fw.append(int(match.group(3)))
	except Exception as ex:
		log += "Trying to find AMC13 firmware version and SN resulted in: {0}\n".format(ex)
	return {
		"sn":			sn,
		"version_sw":	version_sw,
		"version_fw":	version_fw,
		"log":			log,
	}

def print_amc_info():
	amc_info = get_amc_info()
	print "* AMC13  ================================="
	if (amc_info["sn"] == -1):
		print "\tERROR: There was a problem fetching the AMC13 information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(amc_info["log"])
	else:
		print "\tSN: {0}".format(amc_info["sn"])
		print "\tFW version: {0:04d}.{1:04d}".format(amc_info["version_fw"][0], amc_info["version_fw"][1])
		print "\tSW version: {0}".format(amc_info["version_sw"])
#		print "\tLog: {0}".format(amc_info["log"])

def ngccm_command(cmd):
	port = 4242
	raw_output = ""
	if isinstance(cmd, str):
		raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(cmd + "\nquit", port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
		raw_output += raw_output_temp[0] #+ raw_output_temp[1]
	elif isinstance(cmd, list):
		for c in cmd:
			raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(c + "\nquit", port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
			raw_output += raw_output_temp[0] + raw_output_temp[1]
	return raw_output

def get_glib_info():
	data = {
		"version_fw_d": ['get fec1-user_firmware_dd', 0],
		"version_fw_m": ['get fec1-user_firmware_mm', 0],
		"version_fw_y": ['get fec1-user_firmware_yy', 0],
	}
	log = ""
	raw_output = ngccm_command([data[info][0] for info in data.keys()])
	for info in data.keys():
		try:
			match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)		# For some reason the software verion number is printed on stderr...
			data[info][1] = int(match.group(1), 16)
		except Exception as ex:
			log += 'Trying to find the result of "{0}" resulted in: {1}\n'.format(command, ex)
	if (log == ""):
		log = "Empty"
	version_fw = "{0:02d}{1:02d}{2:02d}".format(data["version_fw_y"][1], data["version_fw_m"][1], data["version_fw_d"][1])
	return {
		"version_fw_d":	data["version_fw_d"][1],
		"version_fw_m":	data["version_fw_m"][1],
		"version_fw_y":	data["version_fw_y"][1],
		"version_fw":	version_fw,
		"log":			log,
	}

def print_glib_info():
	glib_info = get_glib_info()
	print "* GLIB   ================================="
	if (glib_info["version_fw"] == "000000"):
		print "\tERROR: There was a problem fetching the GLIB information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(glib_info["log"])
	else:
		print "\tFW version: {0}".format(glib_info["version_fw"])

def get_bridge_info():
	data = {
		"version_fw_major": ['get HF1-2-B_FIRMVERSION_MAJOR', 0],
		"version_fw_minor": ['get HF1-2-B_FIRMVERSION_MINOR', 0],
		"version_fw_svn": ['get HF1-2-B_FIRMVERSION_SVN', 0],
	}
	log = ""
	raw_output = ngccm_command([data[info][0] for info in data.keys()])
	for info in data.keys():
		try:
			match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)		# For some reason the software verion number is printed on stderr...
			data[info][1] = int(match.group(1), 16)
		except Exception as ex:
			log += 'Trying to find the result of "{0}" resulted in: {1}\n'.format(command, ex)
	if (log == ""):
		log = "Empty"
	version_fw = "{0:02d}.{1:02d}.{2:04d}".format(data["version_fw_major"][1], data["version_fw_minor"][1], data["version_fw_svn"][1])
	return {
		"version_fw_major":	data["version_fw_major"][1],
		"version_fw_minor":	data["version_fw_minor"][1],
		"version_fw_svn":	data["version_fw_svn"][1],
		"version_fw":	version_fw,
		"log":			log,
	}

def print_bridge_info():
	bridge_info = get_bridge_info()
	print "* BRIDGE ================================="
	if (bridge_info["version_fw"] == "00.00.0000"):
		print "\tERROR: There was a problem fetching the BRIDGE information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(bridge_info["log"])
	else:
		print "\tFW version: {0}".format(bridge_info["version_fw"])

if __name__ == "__main__":
#	print "=========================================="
	print_amc_info()
	print_glib_info()
	print_bridge_info()
#	print "=========================================="
#	get_bridge_info()
