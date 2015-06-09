####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: This module contains functions for talking to the   #
# AMC13.                                                           #
####################################################################

from re import search
from subprocess import Popen, PIPE
import pexpect

# FUNCTIONS:
def send_commands(ts=False, cmds=[], config=""):		# Sends commands to "AMC13Tool2.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	log = ""
	output = []
	
	if ts:
		# Set up AMC13 configuration path:
		if not config:
			config = "amc13_{0}_config.xml".format(ts.name)		# The default filename.
		config_path = "configuration/{0}".format(config)
		if ("/" in config):
			config_path = config
		
		# Set up list of commands to send:
		if isinstance(cmds, str):		# If you only want to execute one command, you can input it as a string, rather than a list with one element.
			cmds = [cmds]
		cmds.append("q")		# Append the "quit" command to the end of the command list in case it was left off.
		cmds_str = ""
		for c in cmds:
			cmds_str += "{0}\n".format(c)
		
		# Send commands to the AMC13Tool:
		p = pexpect.spawn('AMC13Tool2.exe -c {0}'.format(config_path))
		c_last = False
		raw_output = ""
		log += "----------------------------\nYou ran the following script with the amc13 tool:\n"
		for c in cmds:
			p.expect(">")
			raw_output += p.before
			output.append({
				"cmd": c_last,
				"result": p.before.strip(),
			})
			p.sendline(c)
			c_last = c
			log += c + "\n"
		log += "----------------------------\n"
		p.expect(pexpect.EOF)
		raw_output += p.before
		return {
			"output": output,
			"log": log.strip(),
		}
	else:
		error_msg = "ERROR: \"amc13.send_commands\" needs a teststand object as one of its arguments."
		print ">> " + error_msg
		return {
			"output": "",
			"log": error_msg,
		}

def get_info(ts=False):		# Returns a dictionary of information about the AMC13, such as the FW versions.
	log = ""
	
	if ts:
		version_sw = 0
		version_fw = []
		sn = -1
		results = send_commands(ts=ts, cmds="fv")["output"]
		result = results[0]["result"]
		match = search("Using AMC13 software ver:\s*(\d+)", result)
		if match:
			version_sw = int(match.group(1))
		else:
			log += ">> ERROR: Could not find the SW version.\n"
		result = results[1]["result"]
		match = search("SN:\s+(\d+)\s+T1v:\s+(\d+)\s+T2v:\s+(\d+)", result)
		if match:
			sn = int(match.group(1))
			version_fw.append(int(match.group(2)))
			version_fw.append(int(match.group(3)))
		else:
			log += ">> ERROR: Could not find the SN or the FW version.\n"
		return {
			"sn":			sn,
			"version_sw":	version_sw,
			"version_fw":	version_fw,
			"log":			log.strip(),
		}
	else:
		return {
			"sn":			-1,
			"version_sw":	-1,
			"version_fw":	-1,
			"log":			"",
		}

def get_status(ts=False):
	log = ""
	status = {}
	status["status"] = []
	
	if ts:
		# Ping AMC13 IPs:
		for ip in ts.amc13_ips:
			ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
			if ping_result:
				status["status"].append(1)
			else:
				status["status"].append(0)
		# Make sure the version is accessible:
		amc_info = get_info(ts=ts)
		if (amc_info["sn"] != -1):
			status["status"].append(1)
		else:
			status["status"].append(0)
		# * Add a version check?
		# Use the AMC13Tool.exe to issue "i 1-12":
		results = send_commands(ts=ts, cmds="i 1-12")["output"]
		result = results[1]["result"]
	#	log += amc13_output
		if 'parsed list "1-12" as mask 0xfff\r\nAMC13 out of run mode\r\nAMC13 is back in run mode and ready' in result:
			status["status"].append(1)
		else:
			status["status"].append(0)
		return status
	else:
		return status
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "amc13.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
