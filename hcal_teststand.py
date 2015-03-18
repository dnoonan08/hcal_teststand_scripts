from re import search
from subprocess import Popen, PIPE
import mch
import amc13
import glib
import uhtr
import ngccm
import qie

# FUNCTIONS:

# AMC13 functions are in "amc13.py"
# GLIB functions are in "glib.py"
# uHTR functions are in "uhtr.py"
# ngCCM and ngccm tool functions are in "ngccm.py" (not yet, actually)

# Return the temperatures of your system.
def get_temp(crate, port):		# It's more flexible to not have the input be a teststand object. I should make it accept both.
	log =""
	command = "get HF{0}-adc56_f".format(crate)
	raw_output = ngccm.send_commands(port, command)["output"]
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

# Functions for the whole system (BE and FE):
def get_ts_status(ts):		# This function does basic initializations and checks. If all the "status" bits for each component are 1, then things are good.
	status = {}
	log = ""
	status["mch"] = mch.get_status(ts)
	status["amc13"] = amc13.get_status(ts)
	status["glib"] = glib.get_status(ts)
	status["uhtr"] = uhtr.get_status(ts)
	status["bkp"] = ngccm.get_status_bkp(ts)
	status["ngccm"] = ngccm.get_status(ts)
	status["qie"] = qie.get_status(ts)
	st = []
	for component in ["amc13", "glib", "mch", "uhtr", "bkp", "ngccm", "qie"]:
#		print component
		st_temp = 1
		for s in status[component]["status"]:
			if s != 1:
				st_temp = 0
		st.append(st_temp)
	return {
		"status": st,
		"info": status,
		"log": log,
	}

def parse_ts_configuration(f):		# This function is used to parse the "teststands.txt" configuration file. It is run by the "teststand" class; usually you want to use that instead of running this yourself.
	variables = ["name", "fe_crates", "ngccm_port", "uhtr_ip_base", "uhtr_slots", "glib_slot", "mch_ip", "amc13_ips", "qie_slots"]
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
					elif (variable == "glib_slot"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = int(value)
					elif (variable == "mch_ip"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = value.strip()
					elif (variable == "amc13_ips"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						teststand_info[ts_name][variable] = [i.strip() for i in value.split(",")]
					elif (variable == "qie_slots"):
						value = search("{0}\s*=\s*(.+)".format(variable), line).group(1)
						crate_lists = value.split(";")
						teststand_info[ts_name][variable] = []
						for crate_list in crate_lists:
							if crate_list:
								teststand_info[ts_name][variable].append([int(i) for i in crate_list.split(",")])
							else:
								teststand_info[ts_name][variable].append([])
	return teststand_info
# /FUNCTIONS

# CLASSES:
class teststand:
	# CONSTRUCTION (attribute assignment):
	def __init__(self, *args):
#		if ( (len(args) == 2) and isinstance(args[0], str) and isinstance(args[1], str) ):
		if ( (len(args) == 1) and isinstance(args[0], str) ):
			self.name = args[0]
			f = "teststands.txt"
			ts_info = {}
			try:
				# Exctract teststand info from the teststand configuration file:
				ts_info = parse_ts_configuration(f)[self.name]
#				print ts_info
				for key, value in ts_info.iteritems():
					setattr(self, key, value)
				# Assign a few other calculable attributes:
				self.uhtr_ips = []
				for slot in self.uhtr_slots:
					self.uhtr_ips.append("{0}.{1}".format(self.uhtr_ip_base, slot*4))
				self.glib_ip = "192.168.1.{0}".format(160 + self.glib_slot)
				self.fe = {}
				if len(self.fe_crates) <= len(self.qie_slots):
					for i in range(len(self.fe_crates)):
						self.fe[self.fe_crates[i]] = self.qie_slots[i]
			except Exception as ex:		# The above will fail if the teststand names doesn't appear in the configuration file.
				print "ERROR: Could not read the teststand information for {0} from the configuration file: {1}".format(self.name, f)
				print ">> {0}".format(ex)
		else:
			print "ERROR: You need to initialize a teststand object with a name (string) and a file location for a teststand configuration."
	# METHODS:
	def get_info(self):		# Returns a dictionary of component information, namely versions.
		data = {}
		data["amc13"] = amc13.get_info("amc13_{0}_config.xml".format(self.name))
		data["glib"] = glib.get_info(self.ngccm_port)
		data["uhtr"] = []
		for ip in self.uhtr_ips:
			data["uhtr"].append(uhtr.get_info(ip))
		data["ngccm"] = []
		data["qie"] = []
		for crate, slots in self.fe.iteritems():
			data["ngccm"].append(ngccm.get_info(self.ngccm_port, crate))
			for slot in slots:
				data["qie"].append(qie.get_info(self.ngccm_port, crate, slot))
		return data
	def get_temps(self):		# Returns a list of various temperatures around the teststand.
		temps = []
		for crate in self.fe_crates:
			temps.append(get_temp(crate, self.ngccm_port)["temp"])		# See the "get_temp" funtion above.
		return temps
	def get_status(self):		# Sets up and checks that the teststand is working.
		return get_ts_status(self)
	def set_ped_all(self, n):
		for crate, slots in self.fe:
			for slot in slots:
				qie.set_ped_all(self.ngccm_port, crate, slot, n)
	# /METHODS
	def __str__(self):		# This just defines what the object looks like when it's printed.
		if hasattr(self, "name"):
			return "<teststand object: {0}>".format(self.name)
		else:
			return "<empty teststand object>"
# /CLASSES

# This is what gets exectuted when hcal_teststand.py is executed (not imported).
if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "hcal_teststand.py". This is a module, not a script. See the documentation (readme.md) for more information.'
