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

def print_amc():
	amc_info = get_amc_info()
	print "* AMC13 =================================="
	if (amc_info["sn"] == -1):
		print "\tERROR: There was a problem fetching the AMC13 information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(amc_info["log"])
	else:
		print "\tSN: {0}".format(amc_info["sn"])
		print "\tFW version: {0:04d}.{1:04d}".format(amc_info["version_fw"][0], amc_info["version_fw"][1])
		print "\tSW version: {0}".format(amc_info["version_sw"])
#		print "\tLog: {0}".format(amc_info["log"])

def get_glib_info():
	port = 4242
	commands = 'get fec1-user_firmware_dd\nget fec1-user_firmware_mm\nget fec1-user_firmware_yy\nquit'
	raw_output = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(commands, port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	print raw_output[0]
	print raw_output[1]
#	version_sw = 0
#	version_fw = []
#	sn = -1
#	log = ""
#	try:
#		match = search("Using AMC13 software ver:\s*(\d+)", raw_output[1])		# For some reason the software verion number is printed on stderr...
#		version_sw = int(match.group(1))
#	except Exception as ex:
#		log += "Trying to find AMC13 software version number resulted in: {0}\n".format(ex)
#	try:
#		match = search("SN:\s+(\d+)\s+T1v:\s+(\d+)\s+T2v:\s+(\d+)", raw_output[0].strip())		# Look in stdout for the firmware version.
#		sn = int(match.group(1))
#		version_fw.append(int(match.group(2)))
#		version_fw.append(int(match.group(3)))
#	except Exception as ex:
#		log += "Trying to find AMC13 firmware version and SN resulted in: {0}\n".format(ex)
#	if (log == ""):
#		log = "Empty"
#	return {
#		"sn":			sn,
#		"version_sw":	version_sw,
#		"version_fw":	version_fw,
#		"log":			log,
#	}

if __name__ == "__main__":
	print_amc()
#	get_glib_info()
