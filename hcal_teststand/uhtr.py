# This module contains classes and functions for talking to the uHTR.

from re import search
from subprocess import Popen, PIPE
import hcal_teststand
import qie

# CLASSES:
class link:		# An object that represents a uHTR link. It contains information about what it's connected to.
	qie_half_labels = ['bottom', 'top']
	
	# CONSTRUCTION
	def __init__(self, ts="uknown", uhtr_slot=-1, link_number=-1, qie_unique_id="unknown", qie_half=-1, qie_fiber=-1, on=False):
		self.ts = ts
		self.slot = uhtr_slot
		self.n = link_number
		self.qie_unique_id = qie_unique_id
		self.qie_half = qie_half
		self.qie_half_label = "unknown"
		self.qie_fiber = qie_fiber
		self.on = on
		if self.qie_half in [0, 1]: 
			self.qie_half_label = self.qie_half_labels[self.qie_half]
		self.ip = ""
		if hasattr(ts, "uhtr_ip_base"):
			self.ip = ts.uhtr_ip_base + ".{0}".format(self.slot * 4)
	# /CONSTRUCTION
	
	# METHODS
	def get_data(self):
		print self.ts
		data = get_data_parsed(self.ts, self.slot , 300, self.n)
		if data:
			return data
		else:
			return False
	
	def Print(self):
		print "uHTR Info: Slot {0}, Link {1}".format(self.slot, self.n)
		print "QIE card ID:", self.qie_unique_id
		print "QIE card half:", self.qie_half_label
		print "Fiber:", self.qie_fiber
		print "Active:", (self.on == 1)
	# /METHODS
	
	def __str__(self):		# This just defines what the object looks like when it's printed.
		if self.n != -1:
			return "<link object: uHTR IP = {0}, n = {1}, status = {2}>".format(self.ip, self.n, "on" if self.on else "off")
		else:
			return "<empty link object>"
# /CLASSES

# FUNCTIONS:
def send_commands(ts, uhtr_slot, cmds):		# Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print 'WARNING: You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
		print 'INFO: The "uhtr.send_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	uhtr_cmd = "uHTRtool.exe {0}".format(ts.uhtr[uhtr_slot])
	if hasattr(ts, "control_hub"):
		uhtr_cmd += " -o {0}".format(ts.control_hub)
	raw_output = Popen(['printf "{0}" | {1}'.format(cmds_str, uhtr_cmd)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)

	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def send_commands_script(ts, uhtr_slot, cmds):		# Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print 'WARNING: You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
		print 'INFO: The "uhtr.send_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	uhtr_cmd = "uHTRtool.exe {0}".format(ts.uhtr[uhtr_slot])
	if hasattr(ts, "control_hub"):
		uhtr_cmd += " -o {0}".format(ts.control_hub)
	with open("uhtr_script.cmd", "w") as out:
		out.write(cmds_str)
	raw_output = Popen(['{0} < uhtr_script.cmd'.format(uhtr_cmd)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)

	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def get_info_slot(ts, uhtr_slot):		# Returns a dictionary of information about the uHTR, such as the FW versions.
	log = ""
	data = {	# "HF-4800 (41) 00.0f.00" => FW = [00, 0f, 00], FW_type = [HF-4800, 41] (repeat for "back")
		"version_fw_front": [0, 0, 0],
		"version_fw_type_front": [0, 0],
		"version_fw_back": [0, 0, 0],
		"version_fw_type_back": [0, 0],
	}
	raw_output = send_commands(ts, uhtr_slot, ["0", "exit", "exit"])["output"]
#	log += raw_output
	match = search("Front Firmware revision : (HF-\d+|BHM) \((\d+)\) ([0-9a-f]{2})\.([0-9a-f]{2})\.([0-9a-f]{2})", raw_output)
	if match:
		data["version_fw_type_front"][0] = match.group(1)
		data["version_fw_type_front"][1] = int(match.group(2))
		data["version_fw_front"][0] = int(match.group(3), 16)
		data["version_fw_front"][1] = int(match.group(4), 16)
		data["version_fw_front"][2] = int(match.group(5), 16)
	else:
#		print "Match failed: front version."
		log += '>> ERROR: Failed to find the front FW info.'
	match = search("Back Firmware revision : (HF-\d+|BHM) \((\d+)\) ([0-9a-f]{2})\.([0-9a-f]{2})\.([0-9a-f]{2})", raw_output)
	if match:
		data["version_fw_type_back"][0] = match.group(1)
		data["version_fw_type_back"][1] = int(match.group(2))
		data["version_fw_back"][0] = int(match.group(3), 16)
		data["version_fw_back"][1] = int(match.group(4), 16)
		data["version_fw_back"][2] = int(match.group(5), 16)
	else:
#		print "Match failed: front version."
		log += '>> ERROR: Failed to find the back FW info.'
	return {
		"version_fw_front": data["version_fw_front"],
		"version_fw_type_front": data["version_fw_type_front"],
		"version_fw_back": data["version_fw_back"],
		"version_fw_type_back": data["version_fw_type_back"],
		"version_fw_front_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_front"][0], data["version_fw_front"][1], data["version_fw_front"][2]),
		"version_fw_back_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_back"][0], data["version_fw_back"][1], data["version_fw_back"][2]),
		"slot": uhtr_slot,
		"log": log.strip(),
	}

def get_info(ts):		# A get_info function that accepts either an IP address or a teststand object.
	info = []
	for uhtr_slot in ts.uhtr_slots:
		info.append(get_info_slot(ts, uhtr_slot))
	return info

def get_status(ts):		# Perform basic checks with the uHTRTool.exe:
	status = {}
	status["status"] = []
	# Ping uHTR IPs:
	for ip in ts.uhtr_ips:
		ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
		if ping_result:
			status["status"].append(1)
		else:
			status["status"].append(0)
	# Make sure the versions are accessible:
	for ip in ts.uhtr_ips:
		uhtr_info = get_info(ip)
		if uhtr_info["version_fw_front"][1] != 0:
			status["status"].append(1)
		else:
			status["status"].append(0)
	# Activate links:
	# * Check that there are 6 active links per IP?
	status["links"] = []
	for uhtr_slot in ts.uhtr_slots:
		links = find_links(ts, uhtr_slot)
		status["links"].append(links)
		if links:
			status["status"].append(1)
		else:
			status["status"].append(0)
	return status

def parse_links(raw):		# Parses the raw ouput of the uHTRTool.exe. Commonly, you use the "find_links" function below, which uses this function.
	log = ""
	active = []
	n_times = 0
	for line in raw.split("\n"):
#		print line
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
		log += ">> ERROR: Uh, there were an odd number of \"status\" lines, which is weird."
	return list(set(active))

def parse_links_full(raw):		# Parses the raw ouput of the uHTRTool.exe. Commonly, you use the "find_links" function below, which uses this function.
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
		log += ">> ERROR: Uh, there were an odd number of \"status\" lines, which is weird."
	n_times = 0
	orbit = []
	for line in raw.split("\n"):
		if search("^OrbitRate\(kHz\)", line):
#			print line
			n_times += 1
			orbits = line.split()[1:]
			for i in range(len(orbits)):
				orbit.append( float(orbits[i]) )
	return {
		"active": list(set(active)),
		"orbit": orbit,
	}

def find_links(ts, uhtr_slot):		# Initializes links and then returns a list of link indicies, for a certain uHTR.
	log = ""
	
	# Identify active links:
	commands = [
		'0',
		'link',
		'status',
		'quit',
		'exit',
		'exit',
	]
	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	active_links = parse_links(raw_output)		# A list of the indices of the active links.
	return active_links

def find_links_all(ts):
	result = {}
	for uhtr_slot in ts.uhtr_slots:
		result[uhtr_slot] = find_links(ts, uhtr_slot)
	return result

def find_links_full(ts, uhtr_slot):		# Initializes links and then returns a list of link indicies, for a certain uHTR.
	log = ""
	
	# Identify active links:
	commands = [
		'0',
		'link',
		'status',
		'quit',
		'exit',
		'exit',
	]
	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
#	print raw_output
	log += uhtr_out["log"]
	link_results = parse_links_full(raw_output)		# A list of the indices of the active links.
	return link_results

def get_links(ts, uhtr_slot):		# Initializes and sets up links of a uHTR and then returns a list of links.
	# Set up the QIE card unique IDs:
	is_set = qie.set_unique_id_all(ts)
#	if is_set:
#		print ">> Unique IDs set up."
#	else:
#		print ">> ERROR: Something went wrong setting up the unique IDs."
	
	# Get a list of the active links:
	print "Fetching links from uHTR in slot {0}".format(uhtr_slot)
	active_links = find_links(ts, uhtr_slot)
	print active_links
	
	# For each active link, read QIE unique ID and fiber number from SPY data:
	# (self, uhtr_ip = "unknown", link_number = -1, qie_unique_id = "unknown", qie_half = -1, qie_fiber = -1, on = False)
	hcal_teststand.set_mode_all(ts, 2)
	links = []
	for i in range(24):		# Every uHTR has 24 possible links labeled 0 to 23.
		if i in active_links:
			data = get_data_parsed(ts, uhtr_slot, 50, i)		# Reading fewer than 50 "samples" sometimes results in no data ...
			if data:
#				print data["raw"]
				qie_unique_id = "0x{0}{1} 0x{2}{3}".format(
					data["raw"][0][2][1:5],
					data["raw"][0][1][1:5],
					data["raw"][0][4][1:5],
					data["raw"][0][3][1:5]
				)
				qie_fiber = data["fiber"][0]
				qie_half = data["half"][0]
				links.append(link(ts=ts, uhtr_slot=uhtr_slot, link_number=i, qie_unique_id=qie_unique_id, qie_half=qie_half, qie_fiber=qie_fiber, on = True))
			else:
				links.append(link(ts=ts, on=True))
		else:
			links.append(link(ts=ts, uhtr_slot=uhtr_slot, link_number=i, on=False))
	hcal_teststand.set_mode_all(ts, 0)
	return links

def get_links_all(ts):		# Calls "get_links" for all uHTRs in the system.
	container = {}
	for uhtr_slot in ts.uhtr.keys():
		print "uhtr 283: {0}".format(uhtr_slot)
		container[uhtr_slot] = get_links(ts, uhtr_slot)
	return container

def get_links_all_from_map(ts=False, f="", d="configuration/maps"):		# Returns a list of link objects configured with the data from the uhtr_map.
	links = []
	if ts:
		qie_map = ts.read_qie_map(f=f, d=d)
#		uhtr_info = ts.uhtr_from_qie()
		for qie in [i for i in qie_map if i["channel"] == 0]:
			uhtr_slot = qie["uhtr_slot"]
			link_i = qie["link"]
			links.append(link(
				ts=ts,
				uhtr_slot=uhtr_slot,
				link_number=link_i,
				qie_unique_id=qie["id"],
				qie_half=qie["half"],
				qie_fiber=qie["fiber"],
				on=True
			))
		return links
	else:
		print "ERROR (get_links_from_map): One of the arguments needs to be a teststand object."
		return links

# calls the uHTRs histogramming functionality
# ip - ip address of the uHTR (e.g. teststand("904").uhtr_ips[0])
# n  - number of orbits to integrate over
# sepCapID - whether to distinguish between different cap IDs
# (currently I think this means you can only read out range 0)
# fileName - output file name
def get_histo(ts, uhtr_slot, n , sepCapID , fileName ): 
	
	log = ""
	commands = [
		'0',
		'link',
		'histo',
		'integrate',
		'{0}'.format(n), # number of orbit to integrate over
		'{0}'.format(sepCapID),
		'{0}'.format(fileName),
		'0',
		'quit',
		'quit',
		'exit',
		'exit'
		]
	
	log = send_commands_script(ts, uhtr_slot, commands)["log"]
	# ... seems that send_commands returns a 
	# dictionary which contains all of the outputs

def get_data(ts, uhtr_slot, n, ch):
	log = ""
	
	commands = [
		'0',
		'link',
		'spy',
		'{0}'.format(ch),
		'0',
		'0',
		'{0}'.format(n),
		'quit',
		'exit',
		'exit',
	]
	
	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return uhtr_out

### get triggered data -
def get_triggered_data(ts, uhtr_slot , n , outputFile="testTriggeredData"):
	log = ""

	commands = [
		'0',
		'link',
		'init',
		'1',
		'92',
		'0',
		'0',
		'status',
		'l1acapture',
		'autorun',
		'{0}'.format(n),
		'5',
		'50',
		'0',
		'{0}'.format(outputFile),
		'6,7,8,9',
		'quit',
		'quit',
		'exit',
		'exit',
	]

	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	#return uhtr_out

# Parse uHTRTool.exe data
def parse_data(raw):		# From raw uHTR SPY data, return a list of adcs, cids, etc. organized into sublists per fiber.
#	print raw
	n = 0
	raw_data = []
	for line in raw.split("\n"):
		if search("\s*\d+\s*[0-9A-F]{5}", line):
			raw_data.append(line.strip())
	data = {
		"cid": [],
		"adc": [],
		"tdc_le": [],
		"tdc_te": [],
		"fiber": [],
		"half": [],
		"raw": [],
	}
	raw_temp = []
	for line in raw_data:
		print line
		cid_match = search("CAPIDS", line)
		if cid_match:
			data["cid"].append([int(i) for i in line.split()[-4:]])
		adc_match = search("ADCs", line)
		if adc_match:
			data["adc"].append([int(i) for i in line.split()[-4:]])
		tdc_le_match = search("LE-TDC", line)
		if tdc_le_match:
			data["tdc_le"].append([int(i) for i in line.split()[-4:]])
		tdc_te_match = search("TE-TDC", line)
		if tdc_te_match:
			data["tdc_te"].append([int(i) for i in line.split()[-4:]])
		half_match = search("(TOP|BOTTOM)", line)
		if half_match:
			if half_match.group(1) == "BOTTOM":
				data["half"].append(0)
			elif half_match.group(1) == "TOP":
				data["half"].append(1)
		fiber_match = search("fiber\s([012])", line)
		if fiber_match:
			data["fiber"].append(int(fiber_match.group(1)))
		raw_match = search("\d+\s+([0-9A-F]{5})\s*(.*)", line)
		if raw_match:
			raw_string = raw_match.group(1)
			raw_thing = raw_match.group(2)
			raw_temp.append(raw_string)
			if not raw_thing:
				data["raw"].append(raw_temp)
				raw_temp = []
	data["links"] = parse_links(raw)
	if not data["raw"]:
#		print raw
#		print data
#		print "ERROR: There was no SPY data for some reason."
		return False
	else:
		return data

def get_data_parsed(ts, uhtr_slot, n, ch):
	result = parse_data(get_data(ts, uhtr_slot, n, ch)["output"])
	if result:
		return result
	else:
		print "ERROR: There was no SPY data in the raw uhtr output for uhtr slot {0} and link {1}".format(uhtr_slot, ch)
		return False
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "uhtr.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
