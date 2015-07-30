####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: This test checks the bit error rates of the data    #
# stream.                                                          #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
#import sys
import os
from optparse import OptionParser
from ROOT import *

# FUNCTIONS:
#def create_plots(qie_id):
#	th1 = []
#	for i in range(24):
#		histogram = TH1F("qie{0}".format(i+1), "{0}: QIE {1}".format(qie_id, i+1), 16, -0.5, 15.5)
#		histogram.GetXaxis().CenterTitle(1)
#		histogram.GetXaxis().SetTitle("Clock Phase Setting (~1.6 ns)")
#		histogram.GetYaxis().CenterTitle(1)
#		histogram.GetYaxis().SetTitle("CID Error Rate")
#		histogram.SetLineColor(kRed)
#		histogram.SetFillColor(kRed)
#		th1.append(histogram)
#	return th1

def check_pattern_raw(raw, link_pattern="feed beef"):		# Check the link pattern test data for a single BX of data in a channel.
	if len(raw) == 6:
		string_true = link_pattern
		string = raw[4][1:].lower() + " " + raw[2][1:].lower()		# Chop the leading "0" off and combine into one string.
		counters = [raw[1], raw[3], raw[5]]
		if len(set(counters)) != 1:
			return False
		else:
			if string != string_true:
				return False
			else:
				return True
	else:
		print "ERROR (check_pattern_raw): The raw data had a length of {0}, not 6.".format(len(raw))
		return False

def check_pattern(data):		# Check link pattern test data.
	if len(data) == 4:
		errors = [0 for i in range(4)]
		for ch, d in enumerate(data):
			nbx = len(d)
			if nbx > 0:
				for i_bx in range(nbx):
					result = check_pattern_raw(d[i_bx].raw)
					if not result:
						errors[ch] += 1
			else:
				print "ERROR (check_pattern): The number of bunch crossings recorded for Channel {0} was {1}.".format(ch, nbx)
				return False
		return errors
	else:
		print "ERROR (check_pattern): There wasn't data for all channels in the link."
		return False
# /FUNCTIONS

if __name__ == "__main__":
	# Script arguments:
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is \"157\")",
		metavar="STR"
	)
	parser.add_option("-q", "--qie", dest="qie",
		default="0x67000000 0x9B32C370",
		help="The unique ID of the QIE card you're testing",
		metavar="STR"
	)
	parser.add_option("-v", "--verbose", dest="verbose",
		action="store_true",
		default=False,
		help="Turn on verbose mode (default is off)",
		metavar="BOOL"
	)
	parser.add_option("-o", "--fileName", dest="out",
		default="",
		help="The name of the directory you want to output plots to (default is \"data/ts_904/at_results\").",
		metavar="STR"
	)
	parser.add_option("-n", "--nReads", dest="n",
		default=10,
		help="The number of groups of 100 BXs you want to read per link (defualt is 10).",
		metavar="INT"
	)
	(options, args) = parser.parse_args()
	name = options.ts
	v = options.verbose
	if not options.out:
		path = "data/ts_{0}/at_results/at_bit".format(name)
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/ts_{0}/".format(name) + options.out
	n_reads = int(options.n)
	
	# Set up teststand and print basic info about the test:
	ts = teststand(name)
	log = ""
	t_string = time_string()[:-4]
	print "\n> Running the bit error rate acceptance test ..."
	
	# Set up basic variables for the test:
	crate, slot = ts.crate_slot_from_qie(qie_id=options.qie)
	link_dict = ts.uhtr_from_qie(qie_id=options.qie)
	links = []
	for uhtr_slot, i_links in link_dict.iteritems():
		for i_link in i_links:
			links.append(uhtr.get_link_from_map(ts=ts, uhtr_slot=uhtr_slot, i_link=i_link))
#	th1 = create_plots(options.qie)
	print "\tTeststand: {0}".format(ts.name)
	print "\tQIE card: {0} (crate {1}, slot {2})".format(options.qie, crate, slot)
	
	# Get the teststand ready:
	ts.set_mode(crate=crate, slot=slot, mode=1)		# Turn on link pattern test mode.
	
	# Read data out and check for errors:
	for n_read in range(n_reads):
		for link in links:
			data = link.get_data_spy()
			print data[0][0].raw
			print check_pattern(data)
		
	# Return the teststand to normal:
	ts.set_mode(crate=crate, slot=slot, mode=0)		# Turn off link pattern test mode.
