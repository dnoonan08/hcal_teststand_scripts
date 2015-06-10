####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script logs all BRIDGE, IGLOO2, and nGCCM      #
# registers as well as the power supply and time. This script is   #
# to run continuously, logging at a user set period.               #
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
	directory = "data/logs_157"
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="157",
		help="The name of the teststand you want to use (default is \"157\"). Unless you specify the path, the directory will be put in \"data\".",
		metavar="STR"
	)
	parser.add_option("-o", "--fileName", dest="out",
		default="",
		help="The name of the directory you want to output the logs to (default is \"ts_157\").".format(directory),
		metavar="STR"
	)
	parser.add_option("-T", "--period", dest="T",
		default=1,
		help="The logging period in minutes (default is 1).",
		metavar="INT"
	)
	(options, args) = parser.parse_args()
	name = options.ts
	period = options.T
	if not options.out:
		path = "data/ts_{0}".format(name)
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/" + options.out
	
	ts = teststand(name)
	
	print ">> The output directory is {0}.".format(path)
	print ">> The logging period is {0}.".format(period)
	
	z = True
	while z == True:
		print "[Create log file named \"{0}.log\".]".format(time_string()[:-4])
		z = False
#		sleep(period*60)
	
# /MAIN
