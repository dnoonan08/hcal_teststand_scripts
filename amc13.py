# This module contains functions for talking to the AMC13.

from re import search
from subprocess import Popen, PIPE

# FUNCTIONS:
def send_commands(f, cmds):		# Sends commands to "AMC13Tool2.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	log = ""
	f_temp = ""
	if ("/" in f):
		f_temp = f
	else:
		f_temp = "configuration/{0}".format(f)
	if isinstance(cmds, str):		# If you only want to execute one command, you can input it as a string, rather than a list with one element.
		cmds = [cmds]
	cmds.append("q")		# Append the "quit" command to the end of the command list in case it was left off.
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	raw_output = Popen(['printf "{0}" | AMC13Tool2.exe -c {1}'.format(cmds_str, f_temp)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the commands into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the AMC13Tool:\n\n{0}\n----------------------------".format(cmds_str)
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def get_info(f):		# Returns a dictionary of information about the AMC13, such as the FW versions.
	log = ""
	f_temp = ""
	if ("/" in f):
		f_temp = f
	else:
		f_temp = "configuration/{0}".format(f)
	version_sw = 0
	version_fw = []
	sn = -1
	raw_output = send_commands(f, "fv")["output"]
	match = search("Using AMC13 software ver:\s*(\d+)", raw_output)
	if match:
		version_sw = int(match.group(1))
	else:
		log += ">> ERROR: Could not find the SW version."
	match = search("SN:\s+(\d+)\s+T1v:\s+(\d+)\s+T2v:\s+(\d+)", raw_output)
	if match:
		sn = int(match.group(1))
		version_fw.append(int(match.group(2)))
		version_fw.append(int(match.group(3)))
	else:
		log += ">> ERROR: Could not find the SN or the FW version."
	return {
		"sn":			sn,
		"version_sw":	version_sw,
		"version_fw":	version_fw,
		"log":			log,
	}

def get_status(ts):
	log = ""
	status = {}
	status["status"] = []
	# Ping AMC13 IPs:
	for ip in ts.amc13_ips:
		ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
		if ping_result:
			status["status"].append(1)
		else:
			status["status"].append(0)
	# Use the AMC13Tool.exe to issue "i 1-12":
	amc13_output = send_commands("amc13_{0}_config.xml".format(ts.name), "i 1-12")["output"]
	log += amc13_output
	if 'parsed list "1-12" as mask 0xfff\nAMC13 out of run mode\nAMC13 is back in run mode and ready' in amc13_output:
		status["status"].append(1)
	else:
		status["status"].append(0)
	return status
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "amc13.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
