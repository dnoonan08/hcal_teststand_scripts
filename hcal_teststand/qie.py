# This module contains functions for talking to the QIE card.

from re import search
from subprocess import Popen, PIPE
import ngccm
from time import time, sleep
from numpy import mean, std
import uhtr

# CLASSES:
class qie:
	# Construction:
	def __init__(self, ts=None, unique_id="", crate=-1, slot=-1, n=-1, uhtr_slot=-1, fiber=-1, half=-1, link=-1, channel=-1):
		if not ts:
			ts = None
		self.ts = ts
		self.id = unique_id
		self.crate = crate
		self.slot = slot
		self.n = n
		self.uhtr_slot = uhtr_slot
		self.fiber = fiber
		self.half = half
		self.link = link
		self.channel = channel
	
	# String behavior
	def __str__(self):
		if self.ts:
			return "<qie.qie object: {0}, {1}>".format(self.id, self.n)
		else:
			return "<empty qie.qie object>"
	
	# Methods:
	def get_data(self, method=0):		# Method 0 is for uHTR SPY. Nothing else is implemented, yet.
		if method == 0:
			return uhtr.get_data_parsed_new(self.ts, self.uhtr_slot, 300, self.link)[channel]
		else:
			print "ERROR (qie object {0}): Could not get data because method value {1} wasn't recognized.".format(self.id, method)
			return False
	# /Methods

class datum:
	# Construction:
	def __init__(self, adc=-1, cid=-1, tdc_le=-1, tdc_te=-1, raw=[], raw_uhtr="", bx=-1, ch=-1, half=-1, fiber=-1):
		self.adc = adc
		self.cid = cid
		self.tdc_le = tdc_le
		self.tdc_te = tdc_te
		if not raw:
			raw = []
		self.raw = raw
		self.raw_uhtr = raw_uhtr
		self.bx = bx
		self.ch = ch
		self.half = half
		self.fiber = fiber
	
	# String behavior
	def __str__(self):
		if self.adc != -1:
			return "<qie.datum object>"
		else:
			return "<empty qie.datum object>"
	
	# Methods:
	# /Methods

class status:
	# Construction:
	def __init__(self, ts=None, status=[], crate=-1, slot=-1, fw_top=[], fw_bot="", fw_b=[]):
		if not ts:
			ts = None
		self.ts = ts
		if not status:
			status = []
		self.status = status
		self.crate = crate
		self.slot = slot
		if not fw_top:
			fw_top = []
		self.fw_top = fw_top
		if not fw_bot:
			fw_bot = []
		self.fw_bot = fw_bot
		if not fw_b:
			fw_b = []
		self.fw_b = fw_b
	
	# String behavior
	def __str__(self):
		if self.ts:
			return "<qie.status object: {0}>".format(self.status)
		else:
			return "<empty qie.status object>"
	
	# Methods:
	def update(self):
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
	
	def Print(self, verbose=True):
		if verbose:
			print "[{0}] QIE card in crate {1}, slot {2} status: {3} <- {4}".format(("!!", "OK")[self.good], self.crate, self.slot, ("BAD", "GOOD")[self.good], self.status)
			if self.good:
				print "\tFW IGLOO2 top: {0}".format(self.fw_top)
				print "\tFW IGLOO2 bottom: {0}".format(self.fw_bot)
				print "\tFW bridge: {0}".format(self.fw_b)
		else:
			print "[{0}] QIE card in crate {1}, slot {2} status: {3}".format(("!!", "OK")[self.good], self.crate, self.slot, ("BAD", "GOOD")[self.good])
	
	def log(self):
		output = "%% QIE {0}, {1}\n".format(self.crate, self.slot)
		output += "{0}\n".format(int(self.good))
		output += "{0}\n".format(self.status)
		output += "{0}\n".format(self.fw_top)
		output += "{0}\n".format(self.fw_bot)
		output += "{0}\n".format(self.fw_b)
		return output.strip()
	# /Methods
# /CLASSES

# FUNCTIONS:
# Functions to fetch component information:
def get_bridge_info(ts, crate, slot):		# Returns a dictionary of information about the Bridge FPGA, such as the FW versions.
	data = [
		["version_fw_major", 'get HF{0}-{1}-B_FIRMVERSION_MAJOR'.format(crate, slot), 0],
		["version_fw_minor", 'get HF{0}-{1}-B_FIRMVERSION_MINOR'.format(crate, slot), 0],
		["version_fw_svn", 'get HF{0}-{1}-B_FIRMVERSION_SVN'.format(crate, slot), 0],
	]
	log = ""
	parsed_output = ngccm.send_commands_parsed(ts, [info[1] for info in data])["output"]
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

def get_igloo_info(ts, crate, slot):		# Returns a dictionary of information about the IGLOO2, such as the FW versions.
	data = [
		["version_fw_major_top", 'get HF{0}-{1}-iTop_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		["version_fw_minor_top", 'get HF{0}-{1}-iTop_FPGA_MINOR_VERSION'.format(crate, slot), 0],
		["version_fw_major_bot", 'get HF{0}-{1}-iBot_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		["version_fw_minor_bot", 'get HF{0}-{1}-iBot_FPGA_MINOR_VERSION'.format(crate, slot), 0],
	]
	log = ""
	parsed_output = ngccm.send_commands_parsed(ts, [info[1] for info in data])["output"]
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

def get_info(ts, crate, slot):
	return{
		"bridge": get_bridge_info(ts, crate, slot),
		"igloo": get_igloo_info(ts, crate, slot),
	}

def get_unique_id(ts, crate, slot):		# Reads the unique ID of a given crate and slot and returns it as a list.
	ngccm_output = ngccm.send_commands_parsed(ts, ["get HF{0}-{1}-UniqueID".format(crate,slot)])		# Results in something like "get HF1-1-UniqueID # '1 0x5f000000 0x9b46ce70'"
	result = ngccm_output["output"][0]["result"]
	if "ERROR" not in result: 
		return result.split()[1:3]		# Get the result of the command, and turn the result into a list (ignoring the first element).
	else:
		return []

def get_map(ts, v=False):		# Determines the QIE map of the teststand. A qie map is from QIE crate, slot, qie number to link number, IP, unique_id, etc. It's a list of dictionaries with 3tuples as the keys: (crate, slot, qie)
	# THIS IS A WORK IN PROGRESS. Use get_map_slow until this is fixed.
	print ">> Getting links ..."
	links_by_slot = ts.get_links()
	qie_map = []
	
	# Make sure the teststand is set up:
	print "Disabling fixed-range mode ..."
	ts.set_fixed_range(enable=False)
	
	# Do the mapping:
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			print ">> Mapping crate {0}, slot {1} ...".format(crate, slot)
			for i in range(2):		# Do the following step twice (for QIEs 1-12, and for 13-24).
				print ">> Doing the cycle {0} ...".format(i)
				uhtr_data = []
				ts.set_fixed_range(enable=False, crate=crate, slot=slot)		# Disable fixed-range mode for the card.
				for qie in range(i*12 + 1, i*12 + 13):
					if (v): print "{0} -> {1}".format(qie, int((qie - i*12 - 1)/4) + 1)
					set_fix_range(ts, crate, slot, qie, True, int((qie - i*12 - 1)/4) + 1)
				files_histo = {}
				for uhtr_slot in links_by_slot.keys():
					files_histo[uhtr_slot] = uhtr.get_histo(ts=ts, uhtr_slot=uhtr_slot, sepCapID=0)
					uhtr_data_temp = uhtr.read_histo(files_histo[uhtr_slot])
					temp = {}
					for datum in uhtr_data_temp:
						temp = datum
						temp["uhtr_slot"] = uhtr_slot
						uhtr_data.append(temp)
				
				groups = [[] for j in range(4)]
				for r in range(1, 4):
					for datum in uhtr_data:
						if datum["mean"] > r*64 - 10 and datum["mean"] < r*64 + 10:
#							print datum["mean"]
							groups[r].append(datum)
				
				for r in range(4):
					if len(groups[r]) == 4:
						if len([j["link"] for j in groups[r]]) == 1 and len([j["uhtr_link"] for j in groups[r]]) == 1:
							i_link = groups[r][0]["link"]
							uhtr_slot = groups[r][0]["uhtr_slot"]
						else:
							print "ERROR (qie.get_map): Something is strange about how things are organized ..."
							print groups[r]
					else:
						print "ERROR (qie.get_map): The following group doesn't contain four QIEs"
						print groups[r]
	
	# Make sure the teststand is set up:
	print "Disabling fixed-range mode ..."
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			set_fix_range_all(ts, crate, slot, False)
	
	return qie_map

def get_map_slow(ts):		# Determines the QIE map of the teststand. A qie map is from QIE crate, slot, qie number to link number, IP, unique_id, etc. It's a list of dictionaries with 3tuples as the keys: (crate, slot, qie)
	print "> Getting links ..."
	links_by_uhtr = ts.get_links()
	qie_map = []
	
	# Make sure the teststand is set up:
	print "> Disabling fixed-range mode ..."
	ts.set_fixed_range(enable=False)
	
	# Do the mapping:
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
#			ts.set_fixed_range(crate=crate, slot=slot, enable=False)
			for i_qie in range(1, 25):
				print "> Finding crate {0}, slot {1}, QIE {2} ...".format(crate, slot, i_qie)
				ts.set_fixed_range(crate=crate, slot=slot, i_qie=i_qie, enable=True, r=2)
				channel_save = []
				link_save = []
				for uhtr_slot, links in links_by_uhtr.iteritems():
					for link in [l for l in links if l.on]:
						data = link.get_data_spy()
						if data:
							for channel in range(4):
								adc_avg = mean([d.adc for d in data[channel]])
								print adc_avg
								if adc_avg == 128:
									channel_save.append(channel)
									link_save.append(link)
				if len(channel_save) == 1 and len(link_save):
					channel = channel_save[0]
					link = link_save[0]
					qie_map.append({
						"crate": crate,
						"slot": slot,
						"qie": i_qie,
						"id": link.qie_unique_id,
						"link": link.n,
						"channel": channel,
						"half": link.qie_half,
						"fiber": link.qie_fiber,
						"uhtr_slot": link.slot,
					})
				else:
					if len(channel_save) > 1:
						print "ERROR: Mapping is weird."
					qie_map.append({
						"crate": crate,
						"slot": slot,
						"qie": i_qie,
						"id": [link.qie_unique_id for link in link_save],
						"link": [link.n for link in link_save],
						"channel": channel_save,
						"half": [link.qie_half for link in link_save],
						"fiber": [link.qie_fiber for link in link_save],
						"uhtr_slot": [link.slot for link in link_save],
					})
				ts.set_fixed_range(crate=crate, slot=slot, i_qie=i_qie, enable=False)
	return qie_map
# /

# Functions to set up components:
def set_unique_id(ts, crate, slot):		# Saves the unique ID of a crate slot to the associated QIE card to IGLOO registers.
	unique_id = get_unique_id(ts, crate, slot)
	if unique_id:
		ngccm_output = ngccm.send_commands(ts, [
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
def get_status(ts=None, crate=-1, slot=-1):		# Perform basic checks of the QIE cards:
	log =""
	s = status(ts=ts, crate=crate, slot=slot)
	
#	f_orbit = get_frequency_orbit(ts)
	if ts:
		# Check Bridge FPGA and IGLOO2 version are accessible:
		qie_info = get_info(ts, crate, slot)
		
		## Top:
		s.fw_top = [
			qie_info["igloo"]["version_fw_major_top"],
			qie_info["igloo"]["version_fw_minor_top"],
		]
		if (s.fw_top[0] != 0):
			s.status.append(1)
		else:
			s.status.append(0)
		
		## Bottom:
		s.fw_bot = [
			qie_info["igloo"]["version_fw_major_bot"],
			qie_info["igloo"]["version_fw_minor_bot"],
		]
		if (s.fw_bot[0] != 0):
			s.status.append(1)
		else:
			s.status.append(0)
		
		## Bridge:
		qie_info = get_info(ts, crate, slot)
		s.fw_b = [
			qie_info["bridge"]["version_fw_major"],
			qie_info["bridge"]["version_fw_minor"],
			qie_info["bridge"]["version_fw_svn"]
		]
		if (s.fw_b[0] != 0):
			s.status.append(1)
		else:
			s.status.append(0)
		
		
#		# Check QIE resets in the BRIDGE (1) and the IGLOO2s (2):
#		orbit_temp = []
#		f_orbit_bridge = f_orbit["bridge"][i_qie]
#		f_orbit_igloo = f_orbit["igloo"][i_qie]
#		## (1) Check the BRIDGE:
#		if (f_orbit_bridge["f"] < 13000 and f_orbit_bridge["f"] > 10000 and f_orbit_bridge["f_e"] < 500):
#			status["status"].append(1)
#		else:
#			status["status"].append(0)
#		orbit_temp.append([f_orbit_bridge["f"], f_orbit_bridge["f_e"]])
#		## (2) Check the IGLOO2s:
#		for i in range(2):
#			if (f_orbit_igloo["f"][i] < 13000 and f_orbit_igloo["f"][i] > 10000 and f_orbit_igloo["f_e"][i] < 600):
#				status["status"].append(1)
#			else:
#				status["status"].append(0)
#			orbit_temp.append([f_orbit_igloo["f"][i], f_orbit_igloo["f_e"][i]])
#		status["orbit"].append(orbit_temp)
		s.update()
	return s

def get_status_all(ts=None):
	log = ""
	ss = []
	
	if ts:
		for crate, slots in ts.fe.iteritems():
			for slot in slots:
				ss.append(get_status(ts=ts, crate=crate, slot=slot))
	return ss

def read_counter_qie_bridge(ts, crate, slot):
	log = ""
	count = -1
	cmd = "get HF{0}-{1}-B_RESQIECOUNTER".format(crate, slot)
	output = ngccm.send_commands_parsed(ts, cmd)["output"]
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
	result = ngccm.send_commands_parsed(ts, cmds)
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

# Functions to set IGLOO settings:
## Set IGLOO readout mode:
def set_mode(ts=False, crate=False, slot=False, mode=0):		# 0: normal mode, 1: link test mode A (test mode string), 2: link test mode B (IGLOO register)
#	print ts, crate, slot, mode
	if ts:
		# Parse "mode":
		if mode == 0:
			n = 0
		elif mode == 1:
			n = 1
		elif mode == 2:
			n = 7
		else:
			print "ERROR (qie.set_mode): I don't understand mode = {0}.".format(mode)
			return False
		
		# Build command list:
		cmds = []
		if crate and slot:
			cmds.extend([
				"put HF{0}-{1}-iTop_LinkTestMode 0x{2}".format(crate, slot, n),
				"put HF{0}-{1}-iBot_LinkTestMode 0x{2}".format(crate, slot, n),
				"get HF{0}-{1}-iTop_LinkTestMode".format(crate, slot),
				"get HF{0}-{1}-iBot_LinkTestMode".format(crate, slot),
			])
		else:
			for crate, slots in ts.fe.iteritems():
				for slot in slots:
					cmds.extend([
						"put HF{0}-{1}-iTop_LinkTestMode 0x{2}".format(crate, slot, n),
						"put HF{0}-{1}-iBot_LinkTestMode 0x{2}".format(crate, slot, n),
						"get HF{0}-{1}-iTop_LinkTestMode".format(crate, slot),
						"get HF{0}-{1}-iBot_LinkTestMode".format(crate, slot),
					])
		
		# Send commands:
		output = ngccm.send_commands_parsed(ts, cmds)["output"]
		results = ["ERROR" not in j for j in [i["result"] for i in output]]
		if sum(results) == len(results):
			uhtr.setup_links(ts)		# This initializes all uHTRs' links. This is necessary after changing modes.
			return True
		else:
			print "ERROR (qie.set_mode): Setting the mode resulted in the following:"
			for thing in output:
				print "\t{0} -> {1}".format(thing["cmd"], thing["result"])
			return False
	else:
		print "ERROR (qie.set_mode): You need to include a teststand object as the \"ts\" argument."
		return False

# Functions to set QIE registers:
## Pedestals:
def set_ped(ts=False, crate=False, slot=False, i_qie=set(range(1, 25)), dac=None, dac_cid=None, i_cid=set(range(4))):		# Set the pedestal of QIE "i_qie" to DAC value "dac" and CID DAC value of "dac_cid".
	# Parse "crate" and "slot":
	fe = {}
	if not crate and not slot:
		fe = ts.fe
	elif crate and not slot:
		if isinstance(crate, int):
			crates = [crate]
		elif isinstance(crate, list) or isinstance(crate, set):
			crates = crate
		for i in crates:
			fe[i] = ts.fe[i]
	elif not crate and slot:
		print "ERROR (qie.set_ped): You entered \"slots\" {0}, but no crates. What did you expect to happen? No pedestals were changed.".format(slot)
		return False
	elif crate and slot:
		if isinstance(crate, int):
			crates = [crate]
		elif isinstance(crate, list) or isinstance(crate, set):
			crates = crate
		if isinstance(slot, int):
			slots = [slot]
		elif isinstance(slot, list) or isinstance(slot, set):
			slots = slot
		
		if len(crates) == 1:
			if not isinstance(slots[0], list):
				slots = [slots]
			elif len(slots) > 1:
				print "ERROR (qie.set_ped): The crate/slot configuration is confusing. No pedestals were changed."
				return False
		else:
			if not isinstance(slots[0], list):
				print "ERROR (qie.set_ped): The crate/slot configuration is confusing. No pedestals were changed."
				return False
			else:
				if len(crates) != len(slots):
					print "ERROR (qie.set_ped): The crate/slot configuration is confusing. No pedestals were changed."
					return False
		for i, c in enumerate(crates):
			fe[c] = slots[i]
#	print fe

	# Parse "i_qie":
	i_qie_original = i_qie
	if isinstance(i_qie, int):
		i_qie = [i_qie]
	elif not (isinstance(i_qie, list) or isinstance(i_qie, set)):
		print "ERROR (qie.set_ped): You must enter an integer or a list of integers for \"i_qie\". The pedestals have not be changed."
		return False
	i_qie = set(i_qie)
	if not i_qie.issubset(set(range(1, 25))):
		print "ERROR (qie.set_ped): \"i_qie\" can only contain elements of [1, 2, ..., 24], but you tried to set it to {0}. The pedestals have not be changed.".format(i_qie_original)
		return False
	
	# Parse "i_cid":
	i_cid_original = i_cid
	if isinstance(i_cid, int):
		i_cid = [i_cid]
	elif not (isinstance(i_cid, list) or isinstance(i_cid, set)):
		print "ERROR (qie.set_ped): You must enter an integer or a list of integers for \"i_cid\". The pedestals have not be changed."
		return False
	i_cid = set(i_cid)
	if not i_cid.issubset(set(range(4))):
		print "ERROR (qie.set_ped): \"i_cid\" can only contain elements of [0, 1, 2, 3], but you tried to set it to {0}. The pedestals have not be changed.".format(i_cid_original)
		return False
	
	# Parse "dac" and "dac_cid":
	if dac == None and dac_cid == None:
		print "WARNING (qie.set_ped): You didn't supply a \"dac\" or \"dac_cid\", so \"dac\" will be set to 6, the default, and \"dac_cid\" will be set to 0, the default, for all \"i_cid\" in {0} and all \"i_qie\" in {1}.".format(i_cid, i_qie)
		dac = 6
		dac_cid = 0
	
	## Parse "dac":
	if dac != None:
		if abs(dac) > 31:
			print "ERROR (qie.set_ped): You must enter a decimal integer for \"dac\" between -31 and 31. You tried to set it to {0}. The pedestals have not been changed.".format(dac)
			return False
		else:
			if dac <= 0:
				dac = abs(dac)
			else:
				dac = dac + 32
			dac_str = "{0:#04x}".format(dac)		# The "#" prints the "0x". The number of digits to pad with 0s must include these "0x", hence "4" instead of "2".
	else:
		dac_str = False
	
	## Parse "dac_cid":
	if dac_cid != None:
		if abs(dac_cid) > 7:
			print "ERROR (qie.set_ped): You must enter a decimal integer for \"dac_cid\" between -7 and 7. You tried to set it to {0}. The pedestals have not been changed.".format(dac_cid)
			return False
		else:
			if dac_cid <= 0:
				dac_cid = abs(dac_cid)
			else:
				dac_cid = dac_cid + 8
			dac_cid_str = "{0:#04x}".format(dac_cid)		# The "#" prints the "0x". The number of digits to pad with 0s must include these "0x", hence "4" instead of "2".
	else:
		dac_cid_str = False
	
	# See where things stand:
	if not dac_str and not dac_cid_str:
		print "ERROR (qie.set_ped): You intended to set pedestals, but it turns out none will be changed."
		return False
	if not fe:
		print "ERROR (qie.set_ped): The crate/slot configuration is all jacked up."
		return False
	
	# Build command list:
	cmds = []
	for crate, slots in fe.iteritems():
		for slot in slots:
			for i in i_qie:
				if dac_str:
					cmds.extend([
						"put HF{0}-{1}-QIE{2}_PedestalDAC {3}".format(crate, slot, i, dac_str),
						"get HF{0}-{1}-QIE{2}_PedestalDAC".format(crate, slot, i),
					])
				if dac_cid_str:
					for j in i_cid:
						cmds.extend([
							"put HF{0}-{1}-QIE{2}_CapID{3}pedestal {4}".format(crate, slot, i, j, dac_cid_str),
							"get HF{0}-{1}-QIE{2}_CapID{3}pedestal".format(crate, slot, i, j),
						])
	
	# Send commands:
	output = ngccm.send_commands_parsed(ts, cmds)["output"]
	results = ["ERROR" not in j for j in [i["result"] for i in output]]
	if sum(results) == len(results):
#		for thing in output:
#			print "\t{0} -> {1}".format(thing["cmd"], thing["result"])
		return True
	else:
		print "ERROR (qie.set_ped): Setting pedestals resulted in the following:"
		for thing in output:
			print "\t{0} -> {1}".format(thing["cmd"], thing["result"])
		return False
## /

## Fixed Range Mode:
def set_fixed_range(ts=False, crate=False, slot=False, i_qie=False, enable=False, r=0):		# Turn fixed range mode on or off for a given QIE.
	if ts and isinstance(r, int):
		if r < 0 or r > 3 : 
			print "ERROR (qie.set_fixed_range): The range you select with \"r\" must be an element of {0, 1, 2, 3}."
			return False
		else:
			# Build list of commands:
			cmds = []
			if i_qie:
				if crate and slot:
					if enable:
						cmds.extend([
							"put HF{0}-{1}-QIE{2}_FixRange 1".format(crate, slot, i_qie),
							"put HF{0}-{1}-QIE{2}_RangeSet {3}".format(crate, slot, i_qie, r),
							"get HF{0}-{1}-QIE{2}_FixRange".format(crate, slot, i_qie),
							"get HF{0}-{1}-QIE{2}_RangeSet".format(crate, slot, i_qie),
						])
					else :
						cmds.extend([
							"put HF{0}-{1}-QIE{2}_FixRange 0".format(crate, slot, i_qie),
							"put HF{0}-{1}-QIE{2}_RangeSet 0".format(crate, slot, i_qie),
							"get HF{0}-{1}-QIE{2}_FixRange".format(crate, slot, i_qie),
							"get HF{0}-{1}-QIE{2}_RangeSet".format(crate, slot, i_qie),
						])
				else:
					print "ERROR (qie.set_fixed_range): It's not clear which i_qie = {0} to set, since crate = {1} and slot = {2}.".format(i_qie, crate, slot)
					return False
			else:
				if crate and slot:
					for i_qie in range(1, 25):
						if enable:
							cmds.extend([
								"put HF{0}-{1}-QIE{2}_FixRange 1".format(crate, slot, i_qie),
								"put HF{0}-{1}-QIE{2}_RangeSet {3}".format(crate, slot, i_qie, r),
								"get HF{0}-{1}-QIE{2}_FixRange".format(crate, slot, i_qie),
								"get HF{0}-{1}-QIE{2}_RangeSet".format(crate, slot, i_qie),
							])
						else :
							cmds.extend([
								"put HF{0}-{1}-QIE{2}_FixRange 0".format(crate, slot, i_qie),
								"put HF{0}-{1}-QIE{2}_RangeSet 0".format(crate, slot, i_qie),
								"get HF{0}-{1}-QIE{2}_FixRange".format(crate, slot, i_qie),
								"get HF{0}-{1}-QIE{2}_RangeSet".format(crate, slot, i_qie),
							])
				else:
					for crate, slots in ts.fe.iteritems():
						for slot in slots:
							for i_qie in range(1, 25):
								if enable:
									cmds.extend([
										"put HF{0}-{1}-QIE{2}_FixRange 1".format(crate, slot, i_qie),
										"put HF{0}-{1}-QIE{2}_RangeSet {3}".format(crate, slot, i_qie, r),
										"get HF{0}-{1}-QIE{2}_FixRange".format(crate, slot, i_qie),
										"get HF{0}-{1}-QIE{2}_RangeSet".format(crate, slot, i_qie),
									])
								else :
									cmds.extend([
										"put HF{0}-{1}-QIE{2}_FixRange 0".format(crate, slot, i_qie),
										"put HF{0}-{1}-QIE{2}_RangeSet 0".format(crate, slot, i_qie),
										"get HF{0}-{1}-QIE{2}_FixRange".format(crate, slot, i_qie),
										"get HF{0}-{1}-QIE{2}_RangeSet".format(crate, slot, i_qie),
									])
			
			# Send commands:
			output = ngccm.send_commands_parsed(ts, cmds)["output"]
			results = ["ERROR" not in j for j in [i["result"] for i in output]]
			if sum(results) == len(results):
#				for thing in output:
#					print "\t{0} -> {1}".format(thing["cmd"], thing["result"])
				return True
			else:
				print "ERROR (qie.set_fixed_range): Setting fixed-range mode resulted in the following:"
				for thing in output:
					print "\t{0} -> {1}".format(thing["cmd"], thing["result"])
				return False
	else:
		print "ERROR (qie.set_fixed_range): You need to make sure to input an integer value for \"r\" and a teststand object in \"ts\"."
		return False
## /

## Cal Mode:
def set_cal_mode(ts, crate, slot, qie, enable=False):
	value = 1 if enable else 0
	commands = ["put HF{0}-{1}-QIE{2}_CalMode {3}".format(crate, slot, qie, value)]
	raw_output = ngccm.send_commands_fast(ts, commands)["output"]
#	raw_output = ngccm.send_commands_parsed(ts, commands)["output"]
	return raw_output

def set_cal_mode_all(ts, crate, slot, enable=False):
	commands = []
	value = 1 if enable else 0
	for qie in range(1, 25):
		commands.append("put HF{0}-{1}-QIE{2}_CalMode {3}".format(crate, slot, qie, value))
	raw_output = ngccm.send_commands_fast(ts, commands)["output"]
#	raw_output = ngccm.send_commands_parsed(ts, commands)["output"]
	return raw_output
## /

## QIE clock phase:
def set_clk_phase(ts, crate, slot, qie, phase=0):
	return ngccm.send_commands_parsed(ts, "put HF{0}-{1}-Qie{2}_ck_ph {3}".format(crate, slot, qie, phase))

def set_clk_phase_all(ts, crate, slot, phase=0):
	cmds = ["put HF{0}-{1}-Qie{2}_ck_ph {3}".format(crate, slot, qie, phase) for qie in range(1, 25)]
	return ngccm.send_commands_parsed(ts, cmds)
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
