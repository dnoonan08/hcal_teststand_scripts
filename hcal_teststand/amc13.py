####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: This module contains functions for talking to the   #
# AMC13.                                                           #
####################################################################

from re import search
from subprocess import Popen, PIPE
import pexpect

# CLASSES:
class status:
	# Construction:
	def __init__(self, ts=None, status=[], ips={}, sn=-1, fw=[], sw=-1):
		if not ts:
			ts = None
		self.ts = ts
		if not status:
			status = []
		self.status = status
		if not ips:
			ips = {}
		self.ips = ips
		self.sn = sn
		if not fw:
			fw = []
		self.fw = fw
		self.sw = sw
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
	
	# String behavior
	def __str__(self):
		if self.ts:
			return "<amc13.status object: {0}>".format(self.status)
		else:
			return "<empty amc13.status object>"
	
	# Methods:
	def update(self):
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
	
	def Print(self, verbose=True):
		if verbose:
			print "[{0}] AMC13 status: {1} <- {2}".format(("!!", "OK")[self.good], ("BAD", "GOOD")[self.good], self.status)
			if self.good:
				print "\tSN: {0}".format(self.sn)
				print "\tFW: {0}, {1}".format(self.fw[0], self.fw[1])
				print "\tSW: {0}".format(self.sw)
				print "\tIPs: {0}".format(self.ips)
		else:
			print "[{0}] AMC13 status: {1}".format(("!!", "OK")[self.good], ("BAD", "GOOD")[self.good])
	
	def log(self):
		output = "%% AMC13\n"
		output += "{0}\n".format(int(self.good))
		output += "{0}\n".format(self.status)
		output += "{0}\n".format(self.sn)
		output += "{0}\n".format(self.fw)
		output += "{0}\n".format(self.sw)
		output += "{0}\n".format(self.ips)
		return output.strip()
	# /methods
# /CLASSES

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
		if "q" not in cmds:
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
		print "> " + error_msg
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
			log += ">> ERROR: Could not find the AMC13 SW version.\n"
		result = results[1]["result"]
		match = search("SN:\s+(\d+)\s+T1v:\s+(\d+)\s+T2v:\s+(\d+)", result)
		if match:
			sn = int(match.group(1))
			version_fw.append(int(match.group(2)))
			version_fw.append(int(match.group(3)))
		else:
			log += ">> ERROR: Could not find the AMC13 SN or FW version.\n"
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

def setup(ts=False, mode=0):		# Mode: 0 for normal, 1 for TTC generation.
	log = ""
	output = []
	
	if ts:
		if mode == 0:		# Normal mode.
			results = send_commands(ts=ts, cmds="i 1-12")["output"]
			result = results[1]["result"]
		#	log += amc13_output
			if 'parsed list "1-12" as mask 0xfff\r\nAMC13 out of run mode\r\nAMC13 is back in run mode and ready' in result:
				output.append(1)
			else:
				output.append(0)
			return result
		elif mode == 1:		# TTC mode.
			cmds = [
				"ttc h on",
				"wv CONF.TTC.ENABLE_INTERNAL_L1A 1",
				"wv CONF.TTC.BGO0.COMMAND 0x4",
				"wv CONF.TTC.BGO0.BX 1",
				"wv CONF.TTC.BGO0.ENABLE 1",
				"wv CONF.TTC.ENABLE_BGO 1",
				"i 1-12 t",
#				"q",
			]
			results = send_commands(ts=ts, cmds=cmds)["output"]
			if 'i 1-12 t\r\nparsed list "1-12" as mask 0xfff\r\nEnabling TTS as TTC for loop-back\r\nAMC13 out of run mode\r\nAMC13 is back in run mode and ready' in results[-1]["result"]:
				output.append(1)
			else:
				output.append(0)
			return output
	else:
		return output

def get_status(ts=False, ping=True):		# This should not do anything to the AMC13, but should only be a passive assessment. See "setup".
	log = ""
	s = status(ts=ts)		# Empty amc13.status object
	
	if ts:
		# Ping AMC13 IPs:
		if ping:
			for ip in ts.amc13_ips:
				s.ips[ip] = 0
				ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
				if ping_result:
					s.ips[ip] = 1
					s.status.append(1)
				else:
					s.status.append(0)
		else:
			for ip in ts.amc13_ips:
				s.ips[ip] = -1
		
		# Get versions:
		amc_info = get_info(ts=ts)
		s.sn = amc_info["sn"]
		s.fw = amc_info["version_fw"]
		s.sw = amc_info["version_sw"]
		if (s.sn != -1 and len(s.fw) != 0):
			s.status.append(1)
		else:
			s.status.append(0)
		
		# Update the status object
		s.update()
	return s

#def check_scratch(ts=False, values=['0xffffffff', '0xffffffff', '0xffffffff', '0xffffffff']):
#	if ts:
#		output = ngccm.send_commands
#	else:
#		return False
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "amc13.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
