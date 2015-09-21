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
import os
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
	parser.add_option("-f", "--fast", dest="fast",
		action="store_true",
		default=False,
		help="Turn on fast mode (default is off)",
		metavar="BOOL"
	)
	parser.add_option("-o", "--fileName", dest="out",
		default="",
		help="The name of the directory you want to output the logs to (default is \"ts_157\").",
		metavar="STR"
	)
	(options, args) = parser.parse_args()
	name = options.ts
	v = options.verbose
	fast = options.fast
	if not options.out:
		path = "data/ts_{0}/status".format(name)
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/ts_{0}/".format(name) + options.out
	
	# Set up teststand:
	ts = teststand(name)
	log = ""
	t_string = time_string()[:-4]
	print "\nStatusing the {0} teststand ...".format(ts.name)
	
	# Status the components:
	## AMC13:
	print "(1) Statusing the AMC13s ..."
	amc13_statuses = amc13.get_status(ts=ts, ping=not fast)		# Set "ping" to "False" to ignore pinging the AMC13. (Saves time.)
	for crate, s in amc13_statuses.iteritems():
		s.Print(verbose=v)
		log += s.log()
		log += "\n\n"
	
	## uHTR:
	print "(2) Statusing the uHTRs ..."
	uhtr_statuses = uhtr.get_status(ts=ts, ping=not fast)
	for crate_slot, s in uhtr_statuses.iteritems():
		s.Print(verbose=v)
		log += s.log()
		log += "\n\n"
	
	## BKP:
	print "(3) Statusing the backplanes ..."
	bkp_statuses = bkp.get_status(ts=ts)
	for crate, s in bkp_statuses.iteritems():
		s.Print(verbose=v)
		log += s.log()
		log += "\n\n"
	
	## ngCCM:
	print "(4) Statusing the ngCCMs ..."
	ngccm_statuses = ngccm.get_status(ts=ts)
	for crate, s in ngccm_statuses.iteritems():
		s.Print(verbose=v)
		log += s.log()
		log += "\n\n"
	
	## QIE:
	print "(5) Statusing the QIEs ..."
	qie_statuses = qie.get_status(ts=ts)
	for crate_slot, s in qie_statuses.iteritems():
		s.Print(verbose=v)
		log += s.log()
		log += "\n\n"
	
	# Write out the status log:
	if not os.path.exists(path):
		os.makedirs(path)
	with open("{0}/{1}.log".format(path, t_string), "w") as out:
		out.write(log.strip())
# /MAIN
