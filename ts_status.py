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
	print "\n> Statusing the {0} teststand ...".format(ts.name)
	
	# Status the components:
	## AMC13:
	print "> Statusing the AMC13 ..."
	amc13_status = amc13.get_status(ts=ts, ping=not fast)		# Set "ping" to "False" to ignore pinging the AMC13. (Saves time.)
	amc13_status.Print(verbose=v)
	log += amc13_status.log()
	log += "\n\n"
	
	## uHTR:
	print "\n> Statusing the uHTRs ..."
	uhtr_statuses = uhtr.get_status_all(ts=ts, ping=not fast)
	for uhtr_status in uhtr_statuses:
		uhtr_status.Print(verbose=v)
		log += uhtr_status.log()
		log += "\n\n"
	
	## BKP:
	print "\n> Statusing the backplanes ..."
	bkp_statuses = bkp.get_status_all(ts=ts)
	for bkp_status in bkp_statuses:
		bkp_status.Print(verbose=v)
		log += bkp_status.log()
		log += "\n\n"
	
	## ngCCM:
	print "\n> Statusing the ngCCMs ..."
	ngccm_statuses = ngccm.get_status_all(ts=ts)
	for ngccm_status in ngccm_statuses:
		ngccm_status.Print(verbose=v)
		log += ngccm_status.log()
		log += "\n\n"
	
	## QIE:
	print "\n> Statusing the QIEs ..."
	qie_statuses = qie.get_status_all(ts=ts)
	for qie_status in qie_statuses:
		qie_status.Print(verbose=v)
		log += qie_status.log()
		log += "\n\n"
	
	# Write out the status log:
	if not os.path.exists(path):
		os.makedirs(path)
	with open("{0}/{1}.log".format(path, t_string), "w") as out:
		out.write(log.strip())
# /MAIN
