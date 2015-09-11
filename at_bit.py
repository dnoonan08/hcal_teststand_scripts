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
counter=0

def create_plots(qie_id):
	th1s = {}
	histogram = TH1F("link_pattern", "{0}: Link Pattern Errors".format(qie_id), 24, -0.5, 23.5)
	histogram.GetXaxis().CenterTitle(1)
	histogram.GetXaxis().SetTitle("Channel")
	histogram.GetYaxis().CenterTitle(1)
	histogram.GetYaxis().SetTitle("Link Pattern Error Rate")
	histogram.SetLineColor(kRed)
	histogram.SetFillColor(kRed)
	th1s["link_pattern"] = histogram
	return th1s

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
				counter=int(raw[1],16)
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
			  #		default="0x67000000 0x9B32C370",
			  default="0x9B32C370 0x67000000",
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
		help="The name of the directory you want to output plots to (default is \"data/at_results/[QIE_CARD_ID]\").",
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
		path = "data/at_results/{1}/at_bit".format(name, options.qie.replace(" ", "_"))
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/".format(name) + options.out
	n_reads = int(options.n)
	
	# Set up teststand and print basic info about the test:
	ts = teststand(name)
	log = ""
	t_string = time_string()[:-4]
	print "\n> Running the bit error rate acceptance test ..."
	
	# Set up basic variables for the test:
	crate, slot = ts.crate_slot_from_qie(qie_id=options.qie)
	link_dict = ts.uhtr_from_qie(qie_id=options.qie)
	links=uhtr.get_links_from_map(ts=ts,crate=crate,slot=slot,end='fe')[crate,slot]
	th1s = create_plots(options.qie)
	print "\tTeststand: {0}".format(ts.name)
	print "\tQIE card: {0} (crate {1}, slot {2})".format(options.qie, crate, slot)
	
	# Get the teststand ready:
	ts.set_mode(crate=crate, slot=slot, mode=1)		# Turn on link pattern test mode.
	
	# Read data out and check for errors:
	error_record = {}
	for n_read in range(n_reads):
		print "> Reading data ... ({0}/{1})".format(n_read + 1, n_reads)
		for l, link in enumerate(links):
#			print l, link.n
			data = link.get_data_spy()
#			print data[0][0].raw
			errors = check_pattern(data)
			print errors
			if sum(errors) != 0:
				if link.n not in error_record:
					error_record[link.n] = [0 for i in range(4)]
				error_record[link.n] = [sum(x) for x in zip(error_record[link.n], errors)]
			for ch in range(4):
#				print l*4 + ch, errors[ch]
				th1s["link_pattern"].Fill(l*4 + ch, errors[ch])
	
	# Return the teststand to normal:
	ts.set_mode(crate=crate, slot=slot, mode=0)		# Turn off link pattern test mode.
	
	# Normalize histograms:
	th1s["link_pattern"].Scale(1/(100*float(n_reads)))
	
	# Write output:
	## Write the output ROOT file:
	path += "/" + t_string
	file_name = "{0}/{1}_bit.root".format(path, t_string)
	print "> Saving histograms to {0} ...".format(file_name)
	if not os.path.exists(path):
		os.makedirs(path)
	if os.path.exists(file_name):
		tf = TFile(file_name, "RECREATE")
	else:
		tf = TFile(file_name, "NEW")
	for key, histogram in th1s.iteritems():
		histogram.Write()
	tf.Close()
	
	## Save the plots in a PDF (and SVG):
	gROOT.SetBatch()
	tc = TCanvas("tc", "tc", 500, 500)
	th1s["link_pattern"].Draw()
	th1s["link_pattern"].SetMaximum(1.0)
	th1s["link_pattern"].SetMinimum(0.0)
	tc.SaveAs("{0}/{1}_bit.pdf".format(path, t_string))
	tc.SaveAs("{0}/{1}_bit.svg".format(path, t_string))
	
	# Print a summary:
	print "\n====== SUMMARY ============================"
	print "Teststand: {0}".format(ts.name)
	print "QIE card: {0} (crate {1}, slot {2})".format(options.qie, crate, slot)
	print "BXs read out: {0}".format(100*n_reads)
	if len(error_record.keys()) > 0:
#		print error_record
		print "[!!] Errors: (indexed by channel)"
		for i_link, errors in error_record.iteritems():
			print "\t* Link {0}: error rates = {1}".format(i_link, list_to_string([i/float(100*n_reads) for i in errors]))
	else:
		print "[OK] There were no errors!"
	print "==========================================="
