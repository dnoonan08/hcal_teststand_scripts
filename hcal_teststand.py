from re import search
from subprocess import Popen, PIPE

# This dictionary stores the map between crate number and crate port:
crate_ports = {
	1: 4242,
}

def amc13_commands(ts, cmds):
	log = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	cmds.append("q")
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	raw_output = Popen(['printf "{0}" | AMC13Tool2.exe -c configuration/amc13_config.xml'.format(cmds_str)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the commands into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the AMC13Tool:\n\n{0}\n----------------------------".format(cmds_str)
#	print "========+========"
#	print raw_output[0] + raw_output[1]
#	print "========+========"
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

# uHTR Functions:
def uhtr_commands(ip, cmds):
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print "WARNING: You probably didn't intend to run the uHTRTool with only one command: {0}".format(cmds)
		print 'INFO: The "uhtr_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	raw_output = Popen(['printf "{0}" | uHTRtool.exe {1}'.format(cmds_str, ip)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
#	print "========+========"
#	print raw_output[0] + raw_output[1]
#	print "========+========"
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def uhtr_parse_links(raw):		# Produces a list of activated links from the raw input of the uHTRTool.exe
	log = ""
	active = []
	n_times = 0
	for line in raw.split("\n"):
		if search("^BadCounter(\s*(X|ON)){12}", line):
#			print line
			n_times += 1
			statuses = line.split()[1:]
			for i in range(len(statuses)):
				if statuses[i].strip() == "ON":
					active.append( 12 * ((n_times - 1) % 2) + i )
	if n_times < 2:
		log += ">> ERROR: No correct \"status\" was called on the link."
	elif n_times > 2:
		log += ">> ERROR: Hm, \"status\" was called on the link multiple times, so the active link list might be unreliable. (n_times = {0})".format(n_times)
	if (n_times % 2 != 0):
		log += ">> ERROR: Uh, there were an odd number of \"status\" lines."
	return list(set(active))

def uhtr_get_active_links(ip):
	log = ""
	commands = [
		'0',
		'link',
		'init',
		'1',
		'92',
		'status',
		'quit',
		'exit',
		'exit',
	]
	uhtr_out = uhtr_commands(ip, commands)		# Pass the commands to the uHTR
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return uhtr_parse_links(raw_output)

# ngccm Tool Functions:
def ngccm_commands(crate_port, cmds):		# This executes ngccm commands in the slowest way, in order to read all of the output.
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	for c in cmds:
		raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(c + "\nquit", crate_port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
		raw_output += raw_output_temp[0] + raw_output_temp[1]
	return raw_output

def ngccm_commands_fast(crate_port, cmds):		# This executes ngccm commands in a fast way, but some "get" results might not appear in the output.
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	cmd = ""
	for c in cmds:
		cmd += "{0}\n".format(c)
	cmd += "quit\n"
	raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(cmd, crate_port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
	raw_output += raw_output_temp[0] + raw_output_temp[1]
	return raw_output

# Return the temperatures of your system.
def get_temp(crate, port):		# It's more flexible to not have the input be a teststand object. I should make it accept both.
	log =""
	command = "get HF{0}-adc56_f".format(crate)
	raw_output = ngccm_commands(port, command)
#		print raw_output
	temp = -1
	try:
		match = search("get HF{0}-adc56_f # ([\d\.]+)".format(crate), raw_output)
#			print match.group(0)
#			print match.group(1)
		temp = float(match.group(1))
	except Exception as ex:
#		print raw_output
		log += 'Trying to find the temperature of Crate {0} with "{1}" resulted in: {2}\n'.format(crate, command, ex)
		match = search("\n(.*ERROR!!.*)\n", raw_output)
		if match:
			log+='The data string was "{0}".'.format(match.group(0).strip())
	return {
		"temp":	temp,
		"log":	log,
	}

def get_ts_status(ts):
	status = {}
	log = ""
	# MCH
	# Ping the MCH:
	status["mch"] = {}
	ping_result = Popen(["ping -c 1 {0}".format(ts.mch_ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
	if ping_result:
		status["mch"]["status"] = [1]
	else:
		status["mch"]["status"] = [0]
	# AMC 13
	# Use the AMC13Tool.exe to issue "i 1-12":
	status["amc13"] = {}
	status["amc13"]["status"] = []
	for ip in ts.amc13_ips:
		ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
		if ping_result:
			status["amc13"]["status"].append(1)
		else:
			status["amc13"]["status"].append(0)
	amc13_output = amc13_commands(ts, "i 1-12")["output"]
	log += amc13_output
	if amc13_output:
		status["amc13"]["status"].append(1)
	else:
		status["amc13"]["status"].append(0)
	# GLIB
	# Perform basic checks of the GLIB with the ngccm tool:
	status["glib"] = {}
	ngccm_output = ngccm_commands(ts.ngccm_port, ["get fec1-ctrl", "get fec1-user_wb_regs"])
	log += ngccm_output
	match = search("{0} # ((0x)?[0-9a-f]+)".format("get fec1-ctrl"), ngccm_output)
	if match:
		value = int(match.group(1), 16)
		if (value == int("0x10aa3071", 16)):
			status["glib"]["status"] = [1]
		else:
			log += "ERROR: The result of {0} was {1}, not {2}".format("get fec1-ctrl", value, int("0x10aa3071", 16))
			status["glib"]["status"] = [0]
	else:
		log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get fec1-ctrl")
		status["glib"]["status"] = [0]
	match = search("{0} # '(.*)'".format("get fec1-user_wb_regs"), ngccm_output)
	if match:
		values = match.group(1).split()
		clock = float(int(values[-5], 16))/10000
		status["glib"]["clock"] = clock
		if ( (clock > 40.0640) and (clock < 40.0895) ):
			status["glib"]["status"].append(1)
		else:
			log += "ERROR: The clock frequency of {0} MHz is not between {1} and {2}.".format(clock, 40.0640, 40.0895)
			status["glib"]["status"].append(0)
	else:
		log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get fec1-user_wb_regs")
		status["glib"]["status"].append(0)
	# uHTR
	# Perform basic checks with the uHTRTool.exe:
	status["uhtr"] = {}
	status["uhtr"]["status"] = []
	status["uhtr"]["links"] = []
	for uhtr_ip in ts.uhtr_ips:
		links = uhtr_get_active_links(uhtr_ip)
		status["uhtr"]["links"].append(links)
		if links:
			status["uhtr"]["status"].append(1)
		else:
			status["uhtr"]["status"].append(0)
	# Transition to FE things:
	# BKP (FE Backplane)
	status["bkp"] = {}
	status["bkp"]["status"] = []
	ngccm_output = ngccm_commands_fast(ts.ngccm_port, ["put HF1-bkp_pwr_enable 1", "put HF1-bkp_reset 1", "put HF1-bkp_reset 0"])
	log += ngccm_output
	ngccm_output = ngccm_commands_fast(ts.ngccm_port, "get HF1-bkp_pwr_bad")
	log += ngccm_output
	match = search("{0} # ([01])".format("get HF1-bkp_pwr_bad"), ngccm_output)
	if match:
		status["bkp"]["status"].append((int(match.group(1))+1)%2)
	else:
		log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get HF1-bkp_pwr_bad")
		status["bkp"]["status"].append(0)
	# ngCCM
	# Perform basic checks of the ngCCM:
	status["ngccm"] = {}
	temp = ts.get_temps()[0]
	status["ngccm"]["temp"] = temp
	if (temp != -1) and (temp < 30):
		status["ngccm"]["status"] = [1]
	else:
		status["ngccm"]["status"] = [0]
	return {
		"info": status,
		"log": log
	}

def parse_ts_configuration(f):
	variables = ["name", "fe_crates", "ngccm_port", "uhtr_ip_base", "uhtr_slots", "glib_ip", "mch_ip", "amc13_ips"]
	teststand_info = {}
	raw = ""
	if ("/" in f):
		raw = open("{0}".format(f)).read()
	else:
		raw = open("configuration/{0}".format(f)).read()
	teststands_raw = raw.split("%%")
	for teststand_raw in teststands_raw:
		lines = teststand_raw.strip().split("\n")
		ts_name = ""
		for variable in variables:
			for line in lines:
				if variable in line:
					if (variable == "name"):
						ts_name = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name] = {}
					elif (variable == "fe_crates"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = [int(i) for i in value.split(",")]
					elif (variable == "ngccm_port"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = int(value)
					elif (variable == "uhtr_ip_base"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = value.strip()
					elif (variable == "uhtr_slots"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = [int(i) for i in value.split(",")]
					elif (variable == "glib_ip"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = value.strip()
					elif (variable == "mch_ip"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = value.strip()
					elif (variable == "amc13_ips"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = [i.strip() for i in value.split(",")]
	return teststand_info

class teststand:
	# CONSTRUCTION (attribute assignment):
	def __init__(self, *args):
		if ( (len(args) == 2) and isinstance(args[0], str) and isinstance(args[1], str) ):
			self.name = args[0]
			f = args[1]
			ts_info = {}
			try:
				# Exctract teststand info from the teststand configuration file:
				ts_info = parse_ts_configuration(f)[self.name]
				for key, value in ts_info.iteritems():
					setattr(self, key, value)
				# Assign a few other calculable attributes:
				self.uhtr_ips = []
				for slot in self.uhtr_slots:
					self.uhtr_ips.append("{0}.{1}".format(self.uhtr_ip_base, slot*4))
			except Exception as ex:		# The above will fail if the teststand names doesn't appear in the configuration file.
				print "ERROR: Could not read the teststand information for {0} from the configuration file: {1}".format(self.name, f)
				print ">> {0}".format(ex)
		else:
			print "ERROR: You need to initialize a teststand object with a name (string) and a file location for a teststand configuration."
	# METHODS:
	def get_temps(self):		# A method to return a list of various temperatures around the teststand.
		temps = []
		for crate in self.fe_crates:
			temps.append(get_temp(crate, self.ngccm_port)["temp"])		# See the "get_temp" funtion above.
		return temps
	def status(self):		# A method to setup and check that the teststand is working.
		result = get_ts_status(self)
		status = result["info"]
		log = result["log"]
		print "Status result: {0}".format(status)
		st = [1, 1]
		for key, value in status.iteritems():
			for thing in value["status"]:
				if thing != 1:
					if key in ["amc13", "glib", "mch", "uhtr"]:
						st[0] = 0
					if key in ["bkp", "ngccm", "qie_card"]:
						st[1] = 0
#		print log
		print "Teststand status ({0}):".format(self.name)
		print "[{0}] Back-end".format(st[0])
		print "[{0}] Front-end".format(st[1])
		if sum(st) == len(st):
			print "GOOD"
		else:
			print "BAD"
			print "========== LOG ================================================="
			print log
			print "========== /LOG ================================================"
		return st
	def __str__(self):		# This just defines what the object looks like when it's printed.
		if hasattr(self, "name"):
			return "<teststand object: {0}>".format(self.name)
		else:
			return "<empty teststand object>"

# This is what gets exectuted when hcal_teststand.py is executed (not imported).
if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "hcal_teststand.py". This is a module, not a script. See the documentation (readme.md) for more information.'
