####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script can read and save QIE maps, maps        #
# between link, channel and crate, slot, qie number. Run           #
#      python map_qie.py -h                                        #
# for more documentation.                                          #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys
from os.path import exists
from optparse import OptionParser

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Script arguments:
	directory = "configuration/maps"
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is 904)", metavar="STR")
	parser.add_option("-o", "--fileName", dest="out",
		default="",
		help="The desired filename (it will be saved to {0}). Only use this option if you don't want the default.".format(directory), metavar="STR")
	parser.add_option("-r", "--read", dest="read",
		action="store_true",
		default=False,
		help="Set if you want to read the desired map (set with the -o option).", metavar="BOOL")
	parser.add_option("-s", "--save", dest="save",
		action="store_true",
		default=False,
		help="Set if you want to find and save a new map.", metavar="BOOL")
	(options, args) = parser.parse_args()
	name = options.ts
	if not options.out:
		f_name = "{0}_qie_map.json".format(name)
	else:
		if options.out[-5:] != ".json":
			options.out += ".json"
		f_name = options.out
	
	# Construct the teststand object:
	ts = teststand(name)
	
	# Perform the desired actions:
	if options.save:
		if exists("{0}/{1}".format(directory, f_name)):
			print ">> WARNING: There's already a map for this teststand in {0} called {1}.".format(directory, f_name)
			do = raw_input(">> Do you want to overwrite it with a new one? (y/n)\n")
			if do.lower() == "y" or do.lower() == "yes":
				ts.save_qie_map(f=f_name, d=directory)
			else:
				print ">> Okay, I didn't do anything."
		else:
			print ">> Saving a new map to {0}/{1} ...".format(directory, f_name)
			ts.save_qie_map(f=f_name, d=directory)
	
	if options.read:
		if exists("{0}/{1}".format(directory, f_name)):
			print ">> Reading the map at {0}/{1} ...".format(directory, f_name)
			print ts.read_qie_map(f=f_name, d=directory)
		else:
			print ">> [!!] There's not map at {0}/{1}.".format(directory, f_name)
	
	if not options.read and not options.save:
		print ">> Nothing happened. Run with the -h argument for help."
# /MAIN
