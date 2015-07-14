####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: This module contains functions for talking to the   #
# backplanes.                                                      #
####################################################################

import ngccm

# CLASSES:
class status:
	# Construction:
	def __init__(self, ts=None, status=[], crate=-1, pwr=-1):
		if not ts:
			ts = None
		self.ts = ts
		if not status:
			status = []
		self.status = status
		self.crate = crate
		self.pwr = pwr
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
	
	# String behavior
	def __str__(self):
		if self.ts:
			return "<bkp.status object: {0}>".format(self.status)
		else:
			return "<empty bkp.status object>"
	
	# Methods:
	def update(self):
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
	
	def Print(self, verbose=True):
		if verbose:
			print "[{0}] Backplane of crate {1} status: {2} <- {3}".format(("!!", "OK")[self.good], self.crate, ("BAD", "GOOD")[self.good], self.status)
			if self.good:
				print "\tPWR: {0}".format(("UNKNOWN", "BAD", "GOOD")[self.pwr + 1])
		else:
			print "[{0}] Backplane of crate {1} status: {2}".format(("!!", "OK")[self.good], self.crate, ("BAD", "GOOD")[self.good])
	
	def log(self):
		output = "%% BKP {0}\n".format(self.crate)
		output += "{0}\n".format(int(self.good))
		output += "{0}\n".format(self.status)
		output += "{0}\n".format(self.pwr)
		return output.strip()
	# /methods
# /CLASSES

# FUNCTIONS:
def setup(ts):
	log = []
	output = []
	
	if ts:
		for crate in ts.fe_crates:
			result = True
			cmds = [
				"put HF{0}-bkp_pwr_enable 0".format(crate),
				"put HF{0}-bkp_pwr_enable 1".format(crate),
				"put HF{0}-bkp_reset 1".format(crate),
				"put HF{0}-bkp_reset 0".format(crate),
				"get HF{0}-bkp_pwr_bad".format(crate),
			]
			results = send_commands_parsed(ts, cmds)["output"]
			for cmd in results:
				log.append(cmd)
			for cmd in results[:-1]:
				if "OK" not in cmd["result"]:
					result = False
			if results[-1]["result"] == "1":
				result = False
			output.append(result)
		return {
			"result": output,		# A list of booleans, one for each crate.
			"log": log,		# A list of all ngccm commands sent.
		}
	else:
		return {
			"result": output,
			"log": log,
		}

def get_status(ts=None, crate=-1):		# Perform basic checks of the FE crate backplanes:
	log = ""
	s = status(ts=ts, crate=crate)
	
	if ts:
		# Enable, reset, and check the BKP power:
		if crate in ts.fe_crates:
			ngfec_output = ngccm.send_commands_parsed(ts, "get HF{0}-bkp_pwr_bad".format(crate))["output"]
			if "ERROR" not in ngfec_output[0]["result"]:
				try:
					good = not int(ngfec_output[0]["result"])
					s.pwr = int(good)
					s.status.append(int(good))
				except Exception as ex:
					print ex
					s.status.append(0)
			else:
				s.status.append(0)
		else:
			print "ERROR (bkp.get_status): The crate you want ({0}) is not in the teststand object you supplied.".format(crate)
		s.update()
	return s

def get_status_all(ts=None):
	log = ""
	ss = []
	
	if ts:
		for crate in ts.fe_crates:
			ss.append(get_status(ts=ts, crate=crate))
	return ss
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "bkp.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
