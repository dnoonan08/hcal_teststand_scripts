####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: This module contains functions for talking to the   #
# backplanes.                                                      #
####################################################################

import ngfec
import meta

# CLASSES:
class bkp:
	# Construction:
	def __init__(self, ts=None, crate=None):
		self.ts = ts
		self.crate = crate
	
	# String behavior
	def __str__(self):
		try:
			return "<Backplane in FE Crate {0}>".format(self.crate)
		except Exception as ex:
#			print ex
			return "<empty bkp object>"
	
	# Methods:
	def setup(self, ts=None, verbose=False):
		if ts:
			cmds = [
				"put HF{0}-bkp_pwr_enable 0".format(self.crate),
				"put HF{0}-bkp_pwr_enable 1".format(self.crate),
				"put HF{0}-bkp_reset 1".format(self.crate),
				"put HF{0}-bkp_reset 0".format(self.crate),
				"get HF{0}-bkp_pwr_bad".format(self.crate),
			]
			ngfec_output = ngfec.send_commands(ts=ts, cmds=cmds)
			if verbose: print ngfec_output
			for cmd in ngfec_output[:-1]:
				if "OK" not in cmd["result"]:
					return False
			if ngfec_output[-1]["result"] == "1":
				return False
			return True
		else:
			return False
	# /Methods

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
#def setup(ts=None, crate=None):
#	# Arguments:
#	log = []
#	crates = meta.parse_args_crate(ts=ts, crate=crate)
#	
#	if ts:
#		for crate in crates:
#			cmds = [
#				"put HF{0}-bkp_pwr_enable 0".format(crate),
#				"put HF{0}-bkp_pwr_enable 1".format(crate),
#				"put HF{0}-bkp_reset 1".format(crate),
#				"put HF{0}-bkp_reset 0".format(crate),
#				"get HF{0}-bkp_pwr_bad".format(crate),
#			]
#			ngfec_output = ngccm.send_commands_parsed(ts, cmds)["output"]
##			for cmd in ngfec_output:
##				log.append(cmd)
#			for cmd in ngfec_output[:-1]:
#				if "OK" not in cmd["result"]:
#					return False
#			if ngfec_output[-1]["result"] == "1":
#				return False
#		return True
#	else:
#		return False

def get_status(ts=None, crate=None):		# Perform basic checks of the FE crate backplanes:
	# Arguments:
	log = ""
	crates = meta.parse_args_crate(ts=ts, crate=crate, crate_type="fe")
	if crates:
		statuses = {}
		# Status each crate:
		for fe_crate in crates:
			# Initialize status object
			s = status(ts=ts, crate=fe_crate)
	
			# Enable, reset, and check the BKP power:
			if fe_crate in ts.fe_crates:
				ngfec_output = ngfec.send_commands(ts=ts, cmds=["get HF{0}-bkp_pwr_bad".format(fe_crate)])
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
				print "ERROR (bkp.get_status): The crate you want ({0}) is not in the teststand object you supplied. It has the following crates:\n\t{1}".format(fe_crate, ts.fe_crates)
				return False
			s.update()
			statuses[fe_crate] = s
		return statuses
	else:
		return False
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "bkp.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
