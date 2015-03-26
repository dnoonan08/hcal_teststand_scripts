# This module contains functions for talking to the QIE card.

from re import search
from subprocess import Popen, PIPE
import ngccm
from time import time, sleep
from numpy import mean, std

# FUNCTIONS:
def get_bridge_info(port, crate, slot):		# Returns a dictionary of information about the Bridge FPGA, such as the FW versions.
	data = {
		"version_fw_major": ['get HF{0}-{1}-B_FIRMVERSION_MAJOR'.format(crate, slot), 0],
		"version_fw_minor": ['get HF{0}-{1}-B_FIRMVERSION_MINOR'.format(crate, slot), 0],
		"version_fw_svn": ['get HF{0}-{1}-B_FIRMVERSION_SVN'.format(crate, slot), 0],
	}
	log = ""
	raw_output = ngccm.send_commands(port, [data[info][0] for info in data.keys()])["output"]
	for info in data.keys():
		match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)
		if match:
			data[info][1] = int(match.group(1), 16)
		else:
			log += '>> ERROR: Failed to find the result of "{0}". The data string follows:\n'.format(data[info][0])
			match = search("\n({0}.*)\n".format(data[info][0]), raw_output)
			if match:
				log += '{0}\n'.format(match.group(0).strip())
			else:
				log += "Empty\n"
				log += "{0}\n".format(raw_output)
	version_fw = "{0:02d}.{1:02d}.{2:04d}".format(data["version_fw_major"][1], data["version_fw_minor"][1], data["version_fw_svn"][1])
	return {
		"slot":	slot,
		"version_fw_major":	data["version_fw_major"][1],
		"version_fw_minor":	data["version_fw_minor"][1],
		"version_fw_svn":	data["version_fw_svn"][1],
		"version_fw":	version_fw,
		"log":			log.strip(),
	}

def get_igloo_info(port, crate, slot):		# Returns a dictionary of information about the IGLOO2, such as the FW versions.
	data = {
		"version_fw_major_top": ['get HF{0}-{1}-iTop_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		"version_fw_minor_top": ['get HF{0}-{1}-iTop_FPGA_MINOR_VERSION'.format(crate, slot), 0],
		"version_fw_major_bot": ['get HF{0}-{1}-iBot_FPGA_MAJOR_VERSION'.format(crate, slot), 0],
		"version_fw_minor_bot": ['get HF{0}-{1}-iBot_FPGA_MINOR_VERSION'.format(crate, slot), 0],
	}
	log = ""
	raw_output = ngccm.send_commands(port, [data[info][0] for info in data.keys()])["output"]
	for info in data.keys():
		match = search("{0} # ((0x)?[0-9a-f]+)".format(data[info][0]), raw_output)
		if match:
			data[info][1] = int(match.group(1), 16)
		else:
			log += '>> ERROR: Failed to find the result of "{0}". The data string follows:\n'.format(data[info][0])
			match = search("\n({0}.*)\n".format(data[info][0]), raw_output)
			if match:
				log += '{0}\n'.format(match.group(0).strip())
			else:
				log += "Empty\n"
				log += "{0}\n".format(raw_output)
	version_fw_top = "{0:02d}.{1:02d}".format(data["version_fw_major_top"][1], data["version_fw_minor_top"][1])
	version_fw_bot = "{0:02d}.{1:02d}".format(data["version_fw_major_bot"][1], data["version_fw_minor_bot"][1])
	return {
		"slot": slot,
		"version_fw_major_top":	data["version_fw_major_top"][1],
		"version_fw_minor_top":	data["version_fw_minor_top"][1],
		"version_fw_top":	version_fw_top,
		"version_fw_major_bot":	data["version_fw_major_bot"][1],
		"version_fw_minor_bot":	data["version_fw_minor_bot"][1],
		"version_fw_bot":	version_fw_bot,
		"log":			log.strip(),
	}

def get_info(port, crate, slot):
	return{
		"bridge": get_bridge_info(port, crate, slot),
		"igloo": get_igloo_info(port, crate, slot),
	}

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
		commands = ["put HF{0}-{1}-QIE{2}_PedestalDAC {3}".format(crate, slot, i+1, n_str) for i in range(24)]
		raw_output = ngccm.send_commands_fast(port, commands)["output"]
		# I should include something here to make sure the command didn't return an error? Return 1 if not...

def make_adc_to_q_conversion():
	srs = [
		range(0, 16),
		range(16, 36),
		range(36, 57),
		range(57, 64)
	]
	overlap = 3
	s_init = 3.1			# All other ideal sensitivities can be calculated from this using s = s_init * (8**r) * (2**sr).
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
# /FUNCTIONS


if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "qie.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
