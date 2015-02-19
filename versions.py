from re import search
from subprocess import Popen, PIPE
from hcal_teststand import uhtr_commands, ngccm_commands

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

def get_glib_info(crate_port):
	data = {
		"version_fw_d": ['get fec1-user_firmware_dd', 0],
		"version_fw_m": ['get fec1-user_firmware_mm', 0],
		"version_fw_y": ['get fec1-user_firmware_yy', 0],
	}
	log = ""
	raw_output = ngccm_commands(crate_port, [data[info][0] for info in data.keys()])
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

def print_glib_info(crate_port):
	glib_info = get_glib_info(crate_port)
	print "* GLIB   ================================="
	if (glib_info["version_fw"] == "000000"):
		print "\tERROR: There was a problem fetching the GLIB information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(glib_info["log"])
	else:
		print "\tFW version: {0}".format(glib_info["version_fw"])

def get_uhtr_info(ip):
	data = {	# HF-4800 (41) 00.0f.00 => FW = [00, 0f, 00], FW_type = [HF-4800, 41] (repeat for "back")
		"version_fw_front": [0, 0, 0],
		"version_fw_type_front": [0, 0],
		"version_fw_back": [0, 0, 0],
		"version_fw_type_back": [0, 0],
	}
	log = ""
	raw_output = uhtr_commands(ip, ["0", "exit", "exit"])["output"]
	try:
		match = search("Front Firmware revision : (HF-\d+) \((\d+)\) ([0-9a-f]{2})\.([0-9a-f]{2})\.([0-9a-f]{2})", raw_output)
#		match = search("Front Firmware revision : HF-\d+ \(\d+\) [0-9a-f]{2}\.[0-9a-f]{2}\.[0-9a-f]{2}", raw_output)
		data["version_fw_type_front"][0] = match.group(1)
		data["version_fw_type_front"][1] = int(match.group(2))
		data["version_fw_front"][0] = int(match.group(3), 16)
		data["version_fw_front"][1] = int(match.group(4), 16)
		data["version_fw_front"][2] = int(match.group(5), 16)
	except Exception as ex:
		print "Match failed: 93."
		print ex
		log += 'Trying to find the front FW info resulted in: {0}\n'.format(ex)
	try:
		match = search("Back Firmware revision : (HF-\d+) \((\d+)\) ([0-9a-f]{2})\.([0-9a-f]{2})\.([0-9a-f]{2})", raw_output)
		data["version_fw_type_back"][0] = match.group(1)
		data["version_fw_type_back"][1] = int(match.group(2))
		data["version_fw_back"][0] = int(match.group(3), 16)
		data["version_fw_back"][1] = int(match.group(4), 16)
		data["version_fw_back"][2] = int(match.group(5), 16)
	except Exception as ex:
		print "Match failed: 105."
		print ex
		log += 'Trying to find the back FW info resulted in: {0}\n'.format(ex)
	if (log == ""):
		log = "Empty"
	return {
		"version_fw_front": data["version_fw_front"],
		"version_fw_type_front": data["version_fw_type_front"],
		"version_fw_back": data["version_fw_back"],
		"version_fw_type_back": data["version_fw_type_back"],
		"version_fw_front_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_front"][0], data["version_fw_front"][1], data["version_fw_front"][2]),
		"version_fw_back_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_back"][0], data["version_fw_back"][1], data["version_fw_back"][2]),
		"log": log,
	}

def print_uhtr_info(ip):
	uhtr_info = get_uhtr_info(ip)
	print "* uHTR   ================================="
	print "\tFW version (front): {0}".format(uhtr_info["version_fw_front_str"])
	print "\tFW type (front): {0} ({1})".format(uhtr_info["version_fw_type_front"][0], uhtr_info["version_fw_type_front"][1])
	print "\tFW version (back): {0}".format(uhtr_info["version_fw_back_str"])
	print "\tFW type (back): {0} ({1})".format(uhtr_info["version_fw_type_back"][0], uhtr_info["version_fw_type_back"][1])
	print "\tSW version: ? (it's not currently possible to find out)"

def print_ngccm_info():
#	ngccm_info = get_ngccm_info()
	print "* ngCCM  ================================="
	print "\tFW version (mezzanine): ?"
	print "\tSW version: ?"

def get_bridge_info(crate_port, slot):
	data = {
		"version_fw_major": ['get HF1-{0}-B_FIRMVERSION_MAJOR'.format(slot), 0],
		"version_fw_minor": ['get HF1-{0}-B_FIRMVERSION_MINOR'.format(slot), 0],
		"version_fw_svn": ['get HF1-{0}-B_FIRMVERSION_SVN'.format(slot), 0],
	}
	log = ""
	raw_output = ngccm_commands(crate_port, [data[info][0] for info in data.keys()])
	for info in data.keys():
		try:
			match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)		# For some reason the software verion number is printed on stderr...
			data[info][1] = int(match.group(1), 16)
		except Exception as ex:
			log += 'Trying to find the result of "{0}" resulted in: {1}\n'.format(data[info][0], ex)
	if (log == ""):
		log = "Empty"
	version_fw = "{0:02d}.{1:02d}.{2:04d}".format(data["version_fw_major"][1], data["version_fw_minor"][1], data["version_fw_svn"][1])
	return {
		"slot":	slot,
		"version_fw_major":	data["version_fw_major"][1],
		"version_fw_minor":	data["version_fw_minor"][1],
		"version_fw_svn":	data["version_fw_svn"][1],
		"version_fw":	version_fw,
		"log":			log,
	}

def print_bridge_info(crate_port, slot):
	bridge_info = get_bridge_info(crate_port, slot)
	print "* BRIDGE ================================="
	if (bridge_info["version_fw"] == "00.00.0000"):
		print "\tERROR: There was a problem fetching the BRIDGE information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(bridge_info["log"])
	else:
		print "\tFW version: {0}".format(bridge_info["version_fw"])

def get_igloo_info(crate_port, slot):
	data = {
		"version_fw_major_top": ['get HF1-{0}-iTop_FPGA_MAJOR_VERSION'.format(slot), 0],
		"version_fw_minor_top": ['get HF1-{0}-iTop_FPGA_MINOR_VERSION'.format(slot), 0],
		"version_fw_major_bot": ['get HF1-{0}-iBot_FPGA_MAJOR_VERSION'.format(slot), 0],
		"version_fw_minor_bot": ['get HF1-{0}-iBot_FPGA_MINOR_VERSION'.format(slot), 0],
	}
	log = ""
	raw_output = ngccm_commands(crate_port, [data[info][0] for info in data.keys()])
	for info in data.keys():
		try:
			match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)		# For some reason the software verion number is printed on stderr...
			data[info][1] = int(match.group(1), 16)
		except Exception as ex:
			log += 'Trying to find the result of "{0}" resulted in: {1}\n'.format(data[info][0], ex)
	if (log == ""):
		log = "Empty"
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
		"log":			log,
	}

def print_igloo_info(crate_port, slot):
	igloo_info = get_igloo_info(crate_port, slot)
	print "* IGLOO  ================================="
	if (igloo_info["version_fw_top"] == "00.00"):
		print "\tERROR: There was a problem fetching the IGLOO information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(igloo_info["log"])
	else:
		print "\tFW version (top): {0}".format(igloo_info["version_fw_top"])
		print "\tFW version (bottom): {0}".format(igloo_info["version_fw_bot"])

if __name__ == "__main__":
	crate_port = 4242
	slot = 2
	ip_uhtr = "192.168.29.40"
#	print "=========================================="
	print_amc_info()
	print_glib_info(crate_port)
	print_uhtr_info(ip_uhtr)
	print_ngccm_info()
	print_bridge_info(crate_port, slot)
	print_igloo_info(crate_port, slot)
#	print "=========================================="
#	get_bridge_info()
