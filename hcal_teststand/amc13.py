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
class amc13:
	# Construction:
	def __init__(self, ip_t1=None, ip_t2=None, crate=None, sn=None, fw_t1=None, fw_t2=None, config=None, i_sn=0):
		self.ip_t1 = ip_t1
		self.ip_t2 = ip_t2
		self.crate = crate
		self.sn = sn		# This isn't entirely implemented. Until commandline control hub address specification is added, I can rely on the ordering of the IP addresses for finding the SN when I do "fv" (i_sn).
		self.fw_t1 = fw_t1
		self.fw_t2 = fw_t2
		self.config = config
		self.i_sn = i_sn
		self.ips = [self.ip_t1, self.ip_t2]
		self.fws = self.fw = [self.fw_t1, self.fw_t2]
	
	# String behavior
	def __str__(self):
		try:
			return "<AMC13 in BE Crate {0} with T1 = {1}, T2 = {2}>".format(self.crate, self.ip_t1, self.ip_t2)
		except Exception as ex:
#			print ex
			return "<empty amc13 object>"
	
	# Methods:
	def update(self):
		try:
			info = get_info(config=self.config)[self.i_sn]
			self.sn = info["sn"]
			self.fw_t1 = info["fw_t1"]
			self.fw_t2 = info["fw_t2"]
			self.fws = self.fw = [self.fw_t1, self.fw_t2]
			return True
		except Exception as ex:
			print ex
			return False
	
	def send_commands(self, cmds=None):
		return send_commands(cmds=cmds, config=self.config)
	
	def get_status(self, ping=True):		# This should not do anything to the AMC13 but should only be a passive assessment. See "setup".
		# Prepare:
		if not self.fw_t1:
			self.update()
		
		# Variables:
		s = status()
		
		# Ping AMC13 IPs:
		if ping:
			for ip in self.ips:
				s.ips[ip] = 0
				ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
				if ping_result:
					s.ips[ip] = 1
					s.status.append(1)
				else:
					s.status.append(0)
		else:
			for ip in self.ips:
				s.ips[ip] = -1
				s.status.append(-1)
		
		# Versions:
		if self.fw_t1 and self.fw_t2:
			s.status.append(1)
		else:
			s.status.append(0)
		
		# Update the status object
		s.update()
		return s
	
	def setup(self, mode=0):		# Mode: 0 for normal, 1 for TTC generation.
		# Normal mode:
		if mode == 0:
			results = self.send_commands(cmds="i 1-12")["output"]
			result = results[1]["result"]
		#	log += amc13_output
			if 'parsed list "1-12" as mask 0xfff\r\nAMC13 out of run mode\r\nAMC13 is back in run mode and ready' in result:
				return True
			else:
				return False
		
		# TTC Mode:
		elif mode == 1:
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
			results = self.send_commands(cmds=cmds)["output"]
			if 'i 1-12 t\r\nparsed list "1-12" as mask 0xfff\r\nEnabling TTS as TTC for loop-back\r\nAMC13 out of run mode\r\nAMC13 is back in run mode and ready' in results[-1]["result"]:
				return True
			else:
				return False
		
		# Unknown mode:
		else:
			return False
	# /methods

class status:
	# Construction:
	def __init__(self, ts=None, status=[], ips={}, sn=-1, fw=[], sw=-1):
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
		if self.status:
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
def send_commands(cmds=[], config=""):		# Sends commands to "AMC13Tool2.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	# Arguments and variables:
	## Commands:
	if not cmds:
		print "ERROR (amc13.send_commands): No commands were set to be sent to the AMC13."
		return False
	elif isinstance(cmds, str):		# If you only want to execute one command, you can input it as a string, rather than a list with one element.
		cmds = [cmds]
	if "q" not in cmds:
		cmds.append("q")		# Append the "quit" command to the end of the command list in case it was left off.
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	
	## Configuration:
	if not config:
		print "ERROR (amc13.send_commands): I need to know what AMC13 configuration file to use; none was specified."
		return False
	config_path = "configuration/{0}".format(config)
	if ("/" in config):
		config_path = config
	
	## Other:
	log = ""
	output = []
	
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

def get_info(config=None):		# Returns a dictionary of information about the AMC13, such as the FW versions.
	# Variables:
	log = ""
	info = []
	version_sw = ""
	
	# Get versions from the AMC13:
	results = send_commands(cmds="fv", config=config)["output"]
	if results:
		# Get SW version:
		result = results[0]["result"]
		match = search("Using AMC13 software ver:\s*(\d+)", result)
		if match:
			version_sw = int(match.group(1))
		else:
			print "ERROR (amc13.get_info): Could not find the AMC13 SW version."
			return False
		
		# Get FW versions:
		result = results[1]["result"]
		for line in result.split("\n"):
#			print line
			match = search("SN:\s+(\d+)\s+T1v:\s+(\d+)\s+T2v:\s+(\d+)", line)
			if match:
				sn = int(match.group(1))
				fw_t1 = int(match.group(2))
				fw_t2 = int(match.group(3))
				info.append({
					"sn": sn,
					"fw_t1": fw_t1,
					"fw_t2": fw_t2,
				})
		if not info:
			print "ERROR (amc13.get_info): Could not find the AMC13 FW version."
			return False
		else:
			return info
	else:
		return False

def get_statuses(ts=None, ping=True):
	statuses = {}
	for be_crate, amc13 in ts.amc13s.iteritems():
		statuses[be_crate] = amc13.get_status(ping=ping)
	return statuses

def setup_all(ts=None, mode=0):		# Mode: 0 for normal, 1 for TTC generation.
	results = {}
	for be_crate, amc13 in ts.amc13s.iteritems():
		results[be_crate] = amc13.setup(mode=mode)
	return results

#def check_scratch(ts=False, values=['0xffffffff', '0xffffffff', '0xffffffff', '0xffffffff']):
#	if ts:
#		output = ngccm.send_commands
#	else:
#		return False
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "amc13.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
