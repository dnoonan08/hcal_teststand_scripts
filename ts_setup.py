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

def check_status_uhtr(ts=None, v=False):
	# Get AMC13 statuses:
	statuses = uhtr.get_status(ts=ts)
	
	# Check the AMC13 statuses:
	for crate_slot, s in statuses.iteritems():
		crate, slot = crate_slot
		result = s.status
		if result:
			if result[0]:
				if v: print "\tCan ping the uHTR in BE Crate {0}, BE Slot {1}.".format(crate, slot)
			else:
				print "\t[!!] Can't ping the uHTR in BE Crate {0}, BE Slot {1}.".format(crate, slot)
				return False
			if result[1]:
				if v: print "\tCan fetch FW versions of the uHTR in BE Crate {0}, BE Slot {1}.".format(crate, slot)
			else:
				print "\t[!!] Can't fetch FW versions of the uHTR in BE Crate {0}, BE Slot {1}.".format(crate, slot)
				return False
		else:
			"\t[!!] Couldn't fetch the status of the uHTR in BE Crate {0}, BE Slot {1}.".format(crate, slot)
			return False
	print "\t[OK] All of the uHTRs appear to be functioning."
	return True
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
	print "(3) Setting up the uHTRs ..."
	setup_results = uhtr.setup(ts=ts)
	for crate_slot, setup_result in setup_results.iteritems():
		be_crate, be_slot = crate_slot
		if not setup_result:
			print "\t[!!] Configuration of the uHTR in BE Crate {0}, BE Slot {1} failed.".format(be_crate, be_slot)
			print "Aborting setup ..."
			sys.exit()
		else:
			if v: print "\tuHTR in BE Crate {0}, BE Slot {1} set up.".format(be_crate, be_slot)
	print "\t[OK] Setting up the uHTRs succeeded."
	if not check_status_uhtr(ts=ts, v=v):
		print "\t[!!] Statusing the uHTRs failed."
		print "Aborting setup ..."
		sys.exit()
	
	# Set up the QIEs:
	print "(4) Setting up the QIE cards ..."
# /MAIN
