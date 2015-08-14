####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script performs the basic setup procedure for  #
# the desired teststand.                                           #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
from os.path import exists
from optparse import OptionParser

# CLASSES:
# /CLASSES

# FUNCTIONS:
def check_status_amc13(ts=None, v=False):
	# Get AMC13 statuses:
	statuses = amc13.get_statuses(ts=ts)
	
	# Check the AMC13 statuses:
	for be_crate, s in statuses.iteritems():
		result = s.status
		if result:
			if result[0]:
				if v: print "\tCan ping T1 of the AMC13 in BE Crate {0}.".format(be_crate)
			else:
				print "\t[!!] Can't ping T1 of the AMC13 in BE Crate {0}.".format(be_crate)
				return False
			if result[1]:
				if v: print "\tCan ping T2 of the AMC13 in BE Crate {0}.".format(be_crate)
			else:
				print "\t[!!] Can't ping T1 of the AMC13 in BE Crate {0}.".format(be_crate)
				return False
			if result[2]:
				if v: print "\tCan fetch FW versions of the AMC13 in BE Crate {0}.".format(be_crate)
			else:
				print "\t[!!] Can't fetch FW versions of the AMC13 in BE Crate {0}.".format(be_crate)
				return False
		else:
			"\t[!!] Couldn't fetch the status of the AMC13 in BE Crate {0}.".format(be_crate)
			return False
	print "\t[OK] All of the AMC13s appear to be functioning."
	return True

def check_status_bkp(ts=None, v=False):
	# Get AMC13 status:
	results = [s.status for s in bkp.get_status(ts=ts)]
	
	# Check the AMC13 status:
	if results:
		for result in results:
			if result[0]:
				if v: print "\tBackplane power is good."
			else:
				print "\t[!!] Backplane power is bad."
				return False
		return True
	else:
		"\t[!!] Couldn't fetch the Backplane status."
		return False
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Script arguments:
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is \"157\").",
		metavar="STR"
	)
	parser.add_option("-v", "--verbose", dest="verbose",
		action="store_true",
		default=False,
		help="Turn on verbose mode (default is off)",
		metavar="BOOL"
	)
	(options, args) = parser.parse_args()
	name = options.ts
	v = options.verbose
	
	# Set up teststand:
	ts = teststand(name)
	print "Setting up the {0} teststand ...".format(ts.name)
	
	# Set up the AMC13s:
	print "(1) Setting up the AMC13s ..."
	if check_status_amc13(ts=ts, v=v):
		print "\tConfiguring the AMC13s ..."
		setup_results = amc13.setup_all(ts=ts, mode=1)		# Set up the AMC13s in TTC mode.
		for be_crate, setup_result in setup_results.iteritems():
			if not setup_result:
				print "\t[!!] Configuration of the AMC13 in BE Crate {0} failed.".format(be_crate)
				print "Aborting setup ..."
				sys.exit()
			else:
				if v: print "\tConfigured the AMC13 in BE Crate {0}.".format(be_crate)
		print "\t[OK] Setting up the AMC13s succeeded."
	else:
		print "\t[!!] Statusing the AMC13s failed."
		print "Aborting setup ..."
		sys.exit()
	
	# Set up the FE backplanes:
	print "(2) Setting up the FE backplanes ..."
	setup_results = {}		# Dictionary comprehension was only implemented in Python 2.7 ...
	for fe_crate, b in ts.bkps.iteritems():
		setup_results[fe_crate] = b.setup(ts=ts)
	for fe_crate, setup_result in setup_results.iteritems():
		if not setup_result:
			print "\t[!!] Configuration of the backplane in FE Crate {0} failed.".format(fe_crate)
			print "Aborting setup ..."
			sys.exit()
		else:
			if v: print "\tBackplane in FE Crate {0} powercycled.".format(fe_crate)
			if v: print "\tBackplane in FE Crate {0} reset.".format(fe_crate)
	print "\t[OK] Setting up the backplanes succeeded."
	
	# Set up the uHTRs:
#	if status:
##		if True:
#		print "> Setting up the uHTRs ..."
#		for uhtr_slot in ts.uhtr:
#			print "> Setting up uHTR in slot {0} ...".format(uhtr_slot)
#			cmds = [
#				"0",
#				"clock",
#				"setup",
#				"3",
#				"quit",
#				"link",
#				"init",
#				"1",		# Auto realign
#				"92",		# Orbit delay
#				"0",
#				"0",
#				"quit",
#				"exit",
#				"-1",
#			]
#			output = uhtr.send_commands(ts, uhtr_slot, cmds)["output"]
#			if output:
#				print "> uHTR set up."
#			else:
#				print "> [!!] uHTR failed to set up."
#				status = False
#	if status:
#		print "> [OK] Teststand set up correctly."
#	else:
#		print "> [!!] Set up aborted."
# /MAIN
