# This module contains functions for talking to the uHTR.

from re import search
from subprocess import Popen, PIPE

################################################
# container specifying all of the relevant information
# about the qie that one would need to know about
# a given link 
################################################	
class link : 

	qie_half_label = [ 'bottom' , 'top' ]
	qie_uniqueID = ""
	qie_half     = -1 # see qie_half_label
	qie_fiber    = -1 # either 0,1,2
	on           = False

	def set_link( self , qie_uniqueID_ , qie_half_label_ , qie_fiber_ , on_):

		self.qie_uniqueID = qie_uniqueID_
		self.qie_fiber    = qie_fiber_
		self.on           = on_

		if qie_half_label_ in self.qie_half_label : 
			self.qie_half = self.qie_half_label.index( qie_half_label_ )
		else :
			self.qie_fiber = -1
			print "ERROR: qie_half_label",qie_half_label_,"not known - should be either top or bottom"

	def Print( self ) :
		print "unique ID:",self.qie_uniqueID
		print "board half:",self.qie_half
		print "fiber:",self.qie_fiber
		print "on?",(self.on==1)

	def __init__( self , qie_uniqueID_ = "" , qie_half_label_ = 'bottom' , qie_fiber_ = 0 , on_ = False ):
		
		self.set_link( qie_uniqueID_ , qie_half_label_ , qie_fiber_ , on_ )


################################################
# container to hold QIE mapping for all
# of the links of a given uHTR
# ... eventually, I would like this to 
# read and write xml files so that a snap shot 
# of the cable mapping can be saved 
################################################	
class uHTRlinkMap : 
	
	links = []

	def __init__( self ):
		
		for i in range(96):
			self.links.append( link() )

# FUNCTIONS:

def map_links(ip , outputFile="test.xml") : # looks at the spy dumps of all of the active channels and parses out the QIE card's unique ID and fiber information corresponding
	                         # to the target qie channels

	activeLinks = get_links(ip)
	uhtr_map = uHTRlinkMap()

	for link_ in uhtr_map.links : 
		if uhtr_map.links.index(link_) in activeLinks : 
			#print "link",uhtr_map.links.index(link_),"on..."
			link_.on = True
			# grab spy dump and parse information about this link
			uhtr_read = get_data( ip , 3 , uhtr_map.links.index(link_) )
			data= [""]*6
			for line in uhtr_read["output"].split("\n"):
				#print line
				if line.find("TOP fiber") != -1 : 
					#print line.split(" ")[5]
					data[0] = line.split(" ")[5][1:5]
					link_.qie_half=1
					link_.qie_fiber = int(line.split(" ")[9])
				if line.find("BOTTOM fiber") != -1 : 
					#print line.split(" ")[5]
					data[0] = line.split(" ")[5][1:5]
					link_.qie_half=0
					link_.qie_fiber = int(line.split(" ")[9])
				if line.find("CAPIDS") != -1 :
					data[1] = line.split(" ")[5][1:5]
				if line.find("ADCs") != -1 :
					data[2] = line.split(" ")[5][1:5]
				if line.find("LE-TDC") != -1 :
					data[3] = line.split(" ")[5][1:5]
				if line.find("TE-TDC") != -1 :
					data[4] = line.split(" ")[5][1:5]
				link_.qie_uniqueID = "0x{0}{1}{2}{3} 0x{4}{5}{6}{7}".format(data[2][0:2],data[2][2:4],data[1][0:2],data[1][2:4],data[4][0:2],data[4][2:4],data[3][0:2],data[3][2:4])
			#link_.Print()

	return uhtr_map

def send_commands(ip, cmds):		# Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a IP address and a list of commands.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print 'WARNING: You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
		print 'INFO: The "uhtr.send_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	raw_output = Popen(['printf "{0}" | uHTRtool.exe {1}'.format(cmds_str, ip)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def get_info_ip(ip):		# Returns a dictionary of information about the uHTR, such as the FW versions.
	log = ""
	data = {	# "HF-4800 (41) 00.0f.00" => FW = [00, 0f, 00], FW_type = [HF-4800, 41] (repeat for "back")
		"version_fw_front": [0, 0, 0],
		"version_fw_type_front": [0, 0],
		"version_fw_back": [0, 0, 0],
		"version_fw_type_back": [0, 0],
	}
	raw_output = send_commands(ip, ["0", "exit", "exit"])["output"]
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
	slot = int(ip.split(".")[-1])/4
	return {
		"version_fw_front": data["version_fw_front"],
		"version_fw_type_front": data["version_fw_type_front"],
		"version_fw_back": data["version_fw_back"],
		"version_fw_type_back": data["version_fw_type_back"],
		"version_fw_front_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_front"][0], data["version_fw_front"][1], data["version_fw_front"][2]),
		"version_fw_back_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_back"][0], data["version_fw_back"][1], data["version_fw_back"][2]),
		"slot": slot,
		"log": log.strip(),
	}

def get_info(ip_or_ts):		# A get_info function that accepts either an IP address or a teststand object.
	if isinstance(ip_or_ts, str):
		ip = ip_or_ts
		return get_info_ip(ip)
	else:
		info = []
		ts = ip_or_ts
		for ip in ts.uhtr_ips:
			info.append(get_info_ip(ip))
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
	for ip in ts.uhtr_ips:
		links = get_links(ip)
		status["links"].append(links)
		if links:
			status["status"].append(1)
		else:
			status["status"].append(0)
	return status

def parse_links(raw):		# Parses the raw ouput of the uHTRTool.exe. Commonly, you use the "get_links" function below, which uses this function.
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
	return list(set(active))

def get_links(ip):		# Initializes and then returns a list of the active links of a certain uHTR.
	log = ""
	commands = [
		'0',
		'link',
		'init',
		'1',
		'32',
		'status',
		'quit',
		'exit',
		'exit',
	]
	uhtr_out = send_commands(ip, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return parse_links(raw_output)

# calls the uHTRs histogramming functionality
# ip - ip address of the uHTR (e.g. teststand("904").uhtr_ips[0])
# n  - number of orbits to integrate over
# sepCapID - whether to distinguish between different cap IDs
# (currently I think this means you can only read out range 0)
# fileName - output file name
def get_histo(ip , n , sepCapID , fileName ): 

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

	log = send_commands(ip,commands)["log"]
	# ... seems that send_commands returns a 
	# dictionary which contains all of the outputs

def get_data(ip, n, ch):
	log = ""

	commands = [
		'0',
		'link',
		'init',
		'1',
		'32',
		'status',
		'spy',
		'{0}'.format(ch),
		'0',
		'0',
		'{0}'.format(n),
		'quit',
		'exit',
		'exit',
	]

	uhtr_out = send_commands(ip, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return uhtr_out

# Parse uHTRTool.exe data
def parse_data(raw):		# From raw uHTR SPY data, return a list of adcs, cids, etc. organized into sublists per fiber.
	n = 0
	raw_data = []
	for line in raw.split("\n"):
		if search("\s*\d+\s*[0123456789ABCDEF]{5}", line):
			raw_data.append(line.strip())
	data = {
		"cid": [],
		"adc": [],
		"tdc_le": [],
		"tdc_te": [],
	}
	for line in raw_data:
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
	data["links"] = parse_links(raw)
	return data
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "uhtr.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
