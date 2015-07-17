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
	print "> Setting up the {0} teststand ...".format(ts.name)
	
	# Set up the AMC13:
	print "> Setting up the AMC13 ..."
	result = amc13.get_status(ts=ts).status
	status = True
	if result:
		if result[0]:
			print "> Can ping T1."
		else:
			print "> [!!] Can't ping T1."
			status = False
		if result[1]:
			print "> Can ping T2."
		else:
			print "> [!!] Can't ping T1."
			status = False
		if result[2]:
			print "> Can fetch FW versions."
		else:
			print "> [!!] Can't fetch FW versions."
			status = False
		if status:
			result = amc13.setup(ts=ts, mode=1)		# Set up the AMC13 in TTC mode.
			if result:
				if result[0]:
					print "> Initialization succeeded."
				else:
					print "> [!!] Initialization failed."
					status = False
			else:
				print "> [!!] Initialization failed."
				status = False
			if status:
				print "> [OK] AMC13 set up."
			else:
				print "> [!!] AMC13 failed to set up."
	else:
		print "> [!!] AMC13 failed to set up."
		status = False
	if status:
		print "> Setting up the FE backplane ..."
		output = ngccm.setup(ts=ts)
		results = output["result"]
		if v:
			for cmd in output["log"]:
				print "\t{0} -> {1}".format(cmd["cmd"], cmd["result"])
		for b in results:
			if b:
				print "> Backplane powercycled."
				print "> Backplane reset."
			else:
				status = False
		if status:
			print "> [OK] Backplane set up."
		else:
			print "> [!!] Backplane set up failed."
	if status:
#		if True:
		print "> Setting up the uHTRs ..."
		for uhtr_slot in ts.uhtr:
			print "> Setting up uHTR in slot {0} ...".format(uhtr_slot)
			cmds = [
				"0",
				"clock",
				"setup",
				"3",
				"quit",
				"link",
				"init",
				"1",		# Auto realign
				"92",		# Orbit delay
				"0",
				"0",
				"quit",
				"exit",
				"exit",
			]
			output = uhtr.send_commands(ts, uhtr_slot, cmds)["output"]
			if output:
				print "> uHTR set up."
			else:
				print "> [!!] uHTR failed to set up."
				status = False
	if status:
		print "> [OK] Teststand set up correctly."
	else:
		print "> [!!] Set up aborted."
# /MAIN
