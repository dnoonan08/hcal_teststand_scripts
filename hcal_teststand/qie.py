# This module contains functions for talking to the QIE card.

from re import search
from subprocess import Popen, PIPE
import ngccm
from time import time, sleep
from numpy import mean, std

# CLASSES:
#class qie_card:
#	# CONSTRUCTION:
#	def __init__(self, crate=-1, slot=-1, ts):
#		self.crate = crate
#		self.slot = slot
#		self.ts = ts
#	# /CONSTRUCTION
#	
#	# METHODS:
#	def set_ped(self, n):
#		data = qie.set_ped_all(self.ts.ngccm_port=4242, self.crate, self.slot, n=6)
#		return data
#	# /METHODS
#	
#	def __str__(self):		# This just defines what the object looks like when it's printed.
#		if self.crate != -1:
#			return "<qie card object: crate = {0}, slot = {1}>".format(self.crate, self.slot)
#		else:
#			return "<empty qie card object>"
# /CLASSES

# FUNCTIONS:
# Functions to fetch component information:
def get_bridge_info(port, crate, slot):		# Returns a dictionary of information about the Bridge FPGA, such as the FW versions.
	data = [
		["version_fw_major", 'get HF{0}-{1}-B_FIRMVERSION_MAJOR'.format(crate, slot), 0],
		["version_fw_minor", 'get HF{0}-{1}-B_FIRMVERSION_MINOR'.format(crate, slot), 0],
		["version_fw_svn", 'get HF{0}-{1}-B_FIRMVERSION_SVN'.format(crate, slot), 0],
	]
	log = ""
	parsed_output = ngccm.send_commands_parsed(port, [info[1] for info in data])["output"]
#	print parsed_output
	for info in data:
		result = parsed_output[data.index(info)]["result"]
		cmd = parsed_output[data.index(info)]["cmd"]
		if "ERROR" not in result:
			info[2] = int(result, 16)
		else:
			log += '>> ERROR: Failed to find the result of "{0}". The data string follows:\n{1}'.format(cmd, result)
	version_fw = "{0:02d}.{1:02d}.{2:04d}".format(data[0][2], data[1][2], data[2][2])
	return {
		"slot":	slot,
		"version_fw_major":	data[0][2],
		"version_fw_minor":	data[1][2],
		"version_fw_svn":	data[2][2],
		"version_fw":	version_fw,
		"log":			log.strip(),
	}

def get_igloo_info(port, crate, slot):		# Returns a dictionary of information about the IGLOO2, such as the FW versions.
	data = [
		["version_fw_major_top", 'get HF{0}-{1}-iTop_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		["version_fw_minor_top", 'get HF{0}-{1}-iTop_FPGA_MINOR_VERSION'.format(crate, slot), 0],
		["version_fw_major_bot", 'get HF{0}-{1}-iBot_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		["version_fw_minor_bot", 'get HF{0}-{1}-iBot_FPGA_MINOR_VERSION'.format(crate, slot), 0],
	]
	log = ""
	parsed_output = ngccm.send_commands_parsed(port, [info[1] for info in data])["output"]
#	print parsed_output
	for info in data:
		result = parsed_output[data.index(info)]["result"]
		cmd = parsed_output[data.index(info)]["cmd"]
		if "ERROR" not in result:
			info[2] = int(result, 16)
		else:
			log += '>> ERROR: Failed to find the result of "{0}". The data string follows:\n{1}'.format(cmd, result)
	version_fw_top = "{0:02d}.{1:02d}".format(data[0][2], data[1][2])
	version_fw_bot = "{0:02d}.{1:02d}".format(data[2][2], data[3][2])
	return {
		"slot": slot,
		"version_fw_major_top":	data[0][2],
		"version_fw_minor_top":	data[1][2],
		"version_fw_top":	version_fw_top,
		"version_fw_major_bot":	data[2][2],
		"version_fw_minor_bot":	data[3][2],
		"version_fw_bot":	version_fw_bot,
		"log":			log.strip(),
	}

def get_info(port, crate, slot):
	return{
		"bridge": get_bridge_info(port, crate, slot),
		"igloo": get_igloo_info(port, crate, slot),
	}

def get_unique_id(ts, crate, slot):		# Reads the unique ID of a given crate and slot and returns it as a list.
	ngccm_output = ngccm.send_commands_parsed(ts.ngccm_port, ["get HF{0}-{1}-UniqueID".format(crate,slot)])		# Results in something like "get HF1-1-UniqueID # '1 0x5f000000 0x9b46ce70'"
	result = ngccm_output["output"][0]["result"]
	if "'" in result: 
		return result[1:-1].split()[1:3]		# Get the result of the command, strip the quotes, and turn the result into a list (ignoring the first element).
	else:
		return []

def get_map(ts):		# Determines the QIE map of the teststand. A qie map is from QIE crate, slot, qie number to link number, IP, unique_id, etc. It's a list of dictionaries with 3tuples as the keys: (crate, slot, qie)
	links_by_ip = ts.get_links()
	qie_map = []
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			for qie in range(1, 25):
				print ">> Finding crate {0}, slot {1}, QIE {2} ...".format(crate, slot, qie)
				set_fix_range(ts.ngccm_port, crate, slot, qie, True, 3)
				channel_save = []
				link_save = []
				for ip, links in links_by_ip.iteritems():
					for link in [l for l in links if l.on]:
						data = link.get_data()
						for channel in range(4):
							adc_avg = mean([i_bx[channel] for i_bx in data["adc"]])
#							print adc_avg
							if adc_avg == 192:
								channel_save.append(channel)
								link_save.append(link)
				if len(channel_save) == 1 and len(link_save):
					channel = channel_save[0]
					link = link_save[0]
					qie_map.append({
						"crate": crate,
						"slot": slot,
						"qie": qie,
						"id": link.qie_unique_id,
						"link": link.n,
						"channel": channel,
						"half": link.qie_half,
						"fiber": link.qie_fiber,
						"ip": link.ip,
					})
				else:
					if len(channel_save) > 1:
						print "ERROR: Mapping is weird."
					qie_map.append({
						"crate": crate,
						"slot": slot,
						"qie": qie,
						"id": [link.qie_unique_id for link in link_save],
						"link": [link.n for link in link_save],
						"channel": channel_save,
						"half": [link.qie_half for link in link_save],
						"fiber": [link.qie_fiber for link in link_save],
						"ip": [link.ip for link in link_save],
					})
				set_fix_range(ts.ngccm_port, crate, slot, qie, False)
	return qie_map
# /

# Functions to set up components:
def set_unique_id(ts, crate, slot):		# Saves the unique ID of a crate slot to the associated QIE card to IGLOO registers.
	unique_id = get_unique_id(ts, crate, slot)
	if unique_id:
		ngccm_output = ngccm.send_commands(ts.ngccm_port , [
			"put HF{0}-{1}-iTop_UniqueID {2} {3}".format(crate, slot, unique_id[0], unique_id[1]),
			"put HF{0}-{1}-iBot_UniqueID {2} {3}".format(crate, slot, unique_id[0], unique_id[1])
		])
		return 1
	else:
		return 0

def set_unique_id_all(ts):		# Repeats the "set_unique_id" function from above for all slots in the teststand.
	is_set = []
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			is_set.append(set_unique_id(ts, crate, slot))		# Set the QIE card's unique ID into the correct IGLOO registers.
	if len(set(is_set)) == 1:
		return list(set(is_set))[0]
	else:
		return 0
# /

# Functions to "status" components, including calculating clocks:
def get_status(ts):		# Perform basic checks of the QIE cards:
	status = {}
	status["status"] = []
	status["orbit"] = []
	f_orbit = get_frequency_orbit(ts)
	# Loop over all QIE cards:
	i_qie = -1
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			i_qie += 1
			# Check Bridge FPGA and IGLOO2 version are accessible:
			qie_info = get_info(ts.ngccm_port, crate, slot)
			if (qie_info["bridge"]["version_fw"] != "00.00.0000"):
				status["status"].append(1)
			else:
				status["status"].append(0)
			if (qie_info["igloo"]["version_fw_top"] != "00.00"):
				status["status"].append(1)
			else:
				status["status"].append(0)
			if (qie_info["igloo"]["version_fw_bot"] != "00.00"):
				status["status"].append(1)
			else:
				status["status"].append(0)
			# Check QIE resets in the BRIDGE (1) and the IGLOO2s (2):
			orbit_temp = []
			f_orbit_bridge = f_orbit["bridge"][i_qie]
			f_orbit_igloo = f_orbit["igloo"][i_qie]
			## (1) Check the BRIDGE:
			if (f_orbit_bridge["f"] < 13000 and f_orbit_bridge["f"] > 10000 and f_orbit_bridge["f_e"] < 500):
				status["status"].append(1)
			else:
				status["status"].append(0)
			orbit_temp.append([f_orbit_bridge["f"], f_orbit_bridge["f_e"]])
			## (2) Check the IGLOO2s:
			for i in range(2):
				if (f_orbit_igloo["f"][i] < 13000 and f_orbit_igloo["f"][i] > 10000 and f_orbit_igloo["f_e"][i] < 600):
					status["status"].append(1)
				else:
					status["status"].append(0)
				orbit_temp.append([f_orbit_igloo["f"][i], f_orbit_igloo["f_e"][i]])
			status["orbit"].append(orbit_temp)
	return status

def read_counter_qie_bridge(ts, crate, slot):
	log = ""
	count = -1
	cmd = "get HF{0}-{1}-B_RESQIECOUNTER".format(crate, slot)
	output = ngccm.send_commands_parsed(ts.ngccm_port, cmd)["output"]
	try:
		count = int(output[0]["result"], 16)
	except Exception as ex:
		log += output[0]["cmd"] + " -> " + output[0]["result"] + "\n"
	return {
		"count": count,
		"log": log,
	}
def read_counter_qie_igloo(ts, crate, slot):
	log = ""
	counts = [-1, -1]
	times = [-1, -1]
	cmds = [
		"get HF{0}-{1}-iTop_RST_QIE_count".format(crate, slot),
		"get HF{0}-{1}-iBot_RST_QIE_count".format(crate, slot),
	]
	result = ngccm.send_commands_parsed(ts.ngccm_port, cmds)
	output = result["output"]
	for i in range(2):
		try:
			counts[i] = int(output[i]["result"], 16)
			times[i] = output[i]["times"][0]
		except Exception as ex:
			log += output[i][0] + " -> " + output[i][1] + "\n" + ex + "\n"
	return {
		"counts": counts,
		"times": times,
		"log": log,
	}

def get_frequency_orbit(ts):
	data = {
		"bridge": [],
		"igloo": [],
		"log": "",
	}
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			for fpga in data.keys():
				if fpga == "bridge":
					c = []
					t = []
					for i in range(6):
						result = read_counter_qie_bridge(ts, crate, slot)
						data["log"] += result["log"]
						c.append(result["count"])
						t.append(time())
#						sleep(0.01)
					f = []
					for i in range(len(c)-1):
						f.append((c[i+1]-c[i])/(t[i+1]-t[i]))
					data[fpga].append({
						"f_list":	f,
						"f":	mean(f),
						"f_e":	std(f)/(len(f)**0.5),
					})
				elif fpga == "igloo":
					c = []
					t = []
					for i in range(6):
						result = read_counter_qie_igloo(ts, crate, slot)
						data["log"] += result["log"]
						c.append(result["counts"])
						t.append([result["times"][0], result["times"][1]])
#						sleep(0.01)
					f = []
					for j in range(2):
						f_temp = []
						for i in range(len(c)-1):
							f_temp.append((c[i+1][j]-c[i][j])/(t[i+1][j]-t[i][j]))
						f.append(f_temp)
					data[fpga].append({
						"f_list":	f,
						"f":	[mean(f[0]), mean(f[1])],
						"f_e":	[std(f[0])/(len(f[0])**0.5), std(f[1])/(len(f[1])**0.5)],
					})
	return data
# /

# Functions to set QIE registers:
## Pedestals:
def set_ped(port, crate, slot, i, n):		# Set the pedestal of QIE i to DAC value n.
	assert isinstance(n, int)
	if abs(n) > 31:
		print ">> ERROR: You must enter a decimal integer between -31 and 31. The pedestals have not been changed."
	else:
		if n <= 0:
			n = abs(n)
		else:
			n = n + 32
		n_str = "{0:#04x}".format(n)		# The "#" prints the "0x". The number of digits to pad with 0s must include these "0x", hence "4" instead of "2".
		commands = ["put HF{0}-{1}-QIE{2}_PedestalDAC {3}".format(crate, slot, i, n_str)]
		raw_output = ngccm.send_commands(port, commands)["output"]
		# Maybe I should include something here to make sure the command didn't return an error? Return 1 if not...

def set_ped_all(port, crate, slot, n):		# n is the decimal representation of the pedestal register.
	# This function is faster than running "set_ped" 24 times.
	assert isinstance(n, int)
	if abs(n) > 31:
		print ">> ERROR: You must enter a decimal integer between -31 and 31. The pedestals have not been changed."
	else:
		if n <= 0:
			n = abs(n)
		else:
			n = n + 32
		n_str = "{0:#04x}".format(n)		# The "#" prints the "0x". The number of digits to pad with 0s must include these "0x", hence "4" instead of "2".
		commands = ["put HF{0}-{1}-QIE{2}_PedestalDAC {3}".format(crate, slot, i, n_str) for i in range(1, 25)]
		raw_output = ngccm.send_commands_fast(port, commands)["output"]
		# I should include something here to make sure the command didn't return an error? Return 1 if not...
## /

## Fixed Range Mode:
def set_fix_range(port, crate, slot, qie, enable=False, rangeSet=0):		# Turn fixed range mode on or off for a given QIE.
	assert isinstance(rangeSet, int)
	if rangeSet < 0 or rangeSet > 3 : 
		print ">> ERROR: the range you select with \"RangeSet\" must be an element of {0, 1, 2, 3}."
	else:
		if enable:
			commands = [
				"put HF{0}-{1}-QIE{2}_FixRange 1".format(crate, slot, qie),
				"put HF{0}-{1}-QIE{2}_RangeSet {3}".format(crate, slot, qie, rangeSet)
			]
		else :
			commands = ["put HF{0}-{1}-QIE{2}_FixRange 0".format(crate, slot, qie)]
		
		raw_output = ngccm.send_commands_fast(port, commands)["output"]
#		raw_output = ngccm.send_commands_parsed(port, commands)["output"]
		return raw_output

def set_fix_range_all(port, crate, slot, enable=False, rangeSet=0):		# Turn fixed range mode on or off for all QIEs on a given board.
	assert isinstance(rangeSet, int)
	if rangeSet < 0 or rangeSet > 3: 
		print ">> ERROR: the range you select with \"RangeSet\" must be an element of {0, 1, 2, 3}."
	else:
		commands = []
		if enable:
			for qie in range(1, 25):
				commands.append("put HF{0}-{1}-QIE{2}_FixRange 1".format(crate, slot, qie))
				commands.append("put HF{0}-{1}-QIE{2}_RangeSet {3}".format(crate, slot, qie, rangeSet))
		else:
			for qie in range(1, 25):
				commands.append("put HF{0}-{1}-QIE{2}_FixRange 0".format(crate, slot, qie))
				commands.append("put HF{0}-{1}-QIE{2}_RangeSet 0".format(crate, slot, qie))		# Not necessary, but I think it's probably good form.
		raw_output = ngccm.send_commands_fast(port, commands)["output"]
#		raw_output = ngccm.send_commands_parsed(port, commands)["output"]
		return raw_output
## /

## Cal Mode:
def set_cal_mode(port, crate, slot, qie, enable=False):
	value = 1 if enable else 0
	commands = ["put HF{0}-{1}-QIE{2}_CalMode {3}".format(crate, slot, qie, value)]
	raw_output = ngccm.send_commands_fast(port, commands)["output"]
#	raw_output = ngccm.send_commands_parsed(port, commands)["output"]
	return raw_output

def set_cal_mode_all(port, crate, slot, enable=False):
	commands = []
	value = 1 if enable else 0
	for qie in range(1, 25):
		commands.append("put HF{0}-{1}-QIE{2}_CalMode {3}".format(crate, slot, qie, value))
	raw_output = ngccm.send_commands_fast(port, commands)["output"]
#	raw_output = ngccm.send_commands_parsed(port, commands)["output"]
	return raw_output
## /
# /

# Functions dealing with QIE chip behavior:
def make_adc_to_q_conversion():		# This function generates a list of charge values (in fC) indexed by ADC bin number.
	srs = [		# Subrange information
		range(0, 16),
		range(16, 36),
		range(36, 57),
		range(57, 64)
	]
	overlap = 3		# The number of bins that overlap at range transitions.
	s_init = 3.1		# All other ideal sensitivities can be calculated from this using s = s_init * (8**r) * (2**sr).
	s = 0
	s_sr_min = 0
#	p = -16
	p = 0
	q_sum = p
	q = []
	for r in range(4):
		for sr in range(4):
			for m in srs[sr]:
				s_prev = s
				s = s_init * (8**r) * (2**sr)		# Calculate the appropriate sensitivity.
				q_sum += s_prev/2 + s/2
				if sr == 0 and m == 0 and r > 0:
					q_sum -= s*overlap
				q.append(q_sum)
	return q
# /
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "qie.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
