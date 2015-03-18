# This module contains functions for talking to the ngCCM and the ngccm tool (terribly named).

from re import search
from subprocess import Popen, PIPE

# FUNCTIONS:
def send_commands(port, cmds):		# Executes ngccm commands in the slowest way, in order to read all of the output.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	log += "----------------------------\nYou ran the following script with the ngccm tool:\n"
	for c in cmds:
		log += c + "\nquit\n"
		raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(c + "\nquit", port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
		raw_output += raw_output_temp[0] + raw_output_temp[1]
	log += "----------------------------\n"
	return {
		"output": raw_output,
		"log": log.strip(),
	}

def send_commands_fast(port, cmds):		# This executes ngccm commands in a fast way, but some "get" results might not appear in the output.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	cmds_str += "quit\n"
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
	raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(cmds_str, port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
	raw_output += raw_output_temp[0] + raw_output_temp[1]
	return {
		"output": raw_output,
		"log": log.strip(),
	}

def get_info(port, crate):		# Returns a dictionary of information about the ngCCM, such as the FW versions.
	log =""
	version_fw_mez_major = -1
	version_fw_mez_minor = -1
	cmd = "get HF{0}-mezz_reg4".format(crate)
	raw_output = send_commands(port, cmd)["output"]
	match = search(cmd + " # '((0x)?[0-9a-f]+\s){3}((0x)?[0-9a-f]+)'", raw_output)
	if match:
		version_str_x = "{0:#08x}".format(int(match.group(3),16))
		version_fw_mez_major = int(version_str_x[-2:], 16)
		version_fw_mez_minor = int(version_str_x[-4:-2], 16)
	else:
		log += ">> ERROR: Failed to find FW versions. The data string follows:\n"
		match = search("\n({0}.*)\n".format(cmd), raw_output)
		if match:
			log += 'The data string was "{0}".\n'.format(match.group(0).strip())
		else:
			log += "Empty\n"
			log += "{0}\n".format(raw_output)
	version_fw_mez = "{0:02d}.{1:02d}".format(version_fw_mez_major, version_fw_mez_minor)
	return {
		"version_fw_mez_major":	version_fw_mez_major,
		"version_fw_mez_minor":	version_fw_mez_minor,
		"version_fw_mez":	version_fw_mez,
		"version_sw":	"?",
		"log":			log.strip(),
	}

def get_status(ts):		# Perform basic checks of the ngCCMs:
	status = {}
	status["status"] = []
	# Check that versions are accessible:
	if ts.name != "bhm":
		for crate in ts.fe_crates:
			ngccm_info = get_info(ts.ngccm_port, crate)
			if (ngccm_info["version_fw_mez_major"] != -1):
				status["status"].append(1)
			else:
				status["status"].append(0)
	# Check the temperature:
	temp = ts.get_temps()[0]
	status["temp"] = temp
	if ts.name == "bhm":
		if (temp != -1) and (temp < 30.5):
			status["status"].append(1)
		else:
			status["status"].append(0)
	else:
		if (temp != -1) and (temp < 37):
			status["status"].append(1)
		else:
			status["status"].append(0)
	return status

def get_status_bkp(ts):		# Perform basic checks of the FE crate backplanes:
	log = ""
	status = {}
	status["status"] = []
	# Enable, reset, and check the BKP power:
	for crate in ts.fe_crates:
		ngccm_output = send_commands_fast(ts.ngccm_port, ["put HF{0}-bkp_pwr_enable 1".format(crate), "put HF{0}-bkp_reset 1".format(crate), "put HF{0}-bkp_reset 0".format(crate)])["output"]
		log += ngccm_output
		ngccm_output = send_commands_fast(ts.ngccm_port, "get HF{0}-bkp_pwr_bad".format(crate))["output"]
		log += ngccm_output
		match = search("{0} # ([01])".format("get HF1-bkp_pwr_bad"), ngccm_output)
		if match:
			status["status"].append((int(match.group(1))+1)%2)
		else:
			log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get HF1-bkp_pwr_bad")
			status["status"].append(0)
	return status
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "ngccm.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
