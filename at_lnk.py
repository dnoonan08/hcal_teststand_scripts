####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: This test checks the bit error rates of the data    #
# stream.                                                          #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
import os
from optparse import OptionParser
from ROOT import *

# FUNCTIONS:
def main():
	# Make an acceptance test object:
	at = tests.acceptance(name="lnk")		# Create an acceptance test.
	at.start(False)		# Start the acceptance test by printing some basic things.
	
	# Variables and simple set up:
	ts = at.ts
	qid = at.qid
	links = at.links
	v = at.verbose
	n_reads = at.n		# Number of 100 BX groups to check.
	th1s = create_plots(qid)
	at.canvas.SetCanvasSize(1000, 500)
	at.canvas.Divide(2, 1)
	gStyle.SetOptStat(0)
	
	# (1) Verify link pattern test:
	print "(1) Performing a link pattern test ..."
	# Get the teststand ready:
	mode_result = ts.set_mode(mode=1)		# Turn on link pattern test mode.
	if not mode_result:
		print "\tERROR (at_lnk.main): Could not turn link pattern test mode on."
		print "\t[!!] Acceptance test aborted."
		sys.exit()
	
	# Read data out and check for errors:
	error_record = {}
	for n_read in range(n_reads):
		print "\tReading link pattern data ... ({0}/{1})".format(n_read + 1, n_reads)
		for l, link in enumerate(links):
#			print l, link.n
			data = link.get_data_spy(n_bx=300)
#			print data[0][0].raw
			errors = check_pattern(data)
			if errors != 0:
				if link.n not in error_record:
					error_record[link.n] = 0
				error_record[link.n] += errors
				th1s["link_pattern"].Fill(l, errors)
	
	# Return the teststand to normal:
	mode_result = ts.set_mode(mode=0)		# Turn off link pattern test mode.
	if not mode_result:
		print "\tWARNING (at_lnk.main): Could not turn link pattern test mode off."
		print "\t[!!] Acceptance test aborted."
		sys.exit()
		
	# Normalize histograms:
	th1s["link_pattern"].Scale(1/(100*float(n_reads)))
	# /(1)
	
	# (2) Read link error rates from the uHTR:
	print "(2) Reading link error rates from the uHTR ..."
	errdata = uhtr.parse_err(uhtr.get_raw_err(ts=ts, crate=at.be_crate, slot=at.be_slot))
#	print errdata
#	print '\n >> bad data test:'
	for i_link, value in errdata.iteritems():
#		print 'Link {0}: BadDataRate {1}'.format(i_link, value)
		th1s["uhtr_error"].Fill(i_link%6, value)
#	print "==========================================="
	# /(2)
	
	# Write output:
	## Write to the output ROOT file:
	for key, histogram in th1s.iteritems():
		histogram.Write()
	
	## Save the plots:
	at.canvas.cd(1)
	th1s["link_pattern"].Draw()
	gPad.SetLogy(1)
	th1s["link_pattern"].SetMaximum(1.0)
#	th1s["link_pattern"].SetMinimum(0.0)
	at.canvas.cd(2)
	th1s["uhtr_error"].Draw()
	gPad.SetLogy(1)
	th1s["uhtr_error"].SetMaximum(1.0)
#	th1s["uhtr_error"].SetMinimum(0.0)
	
	## Ask the acceptance test object to save everything:
	at.write()
	
	# Print a summary:
	print "\n====== SUMMARY ============================"
	print "Teststand: {0}".format(ts.name)
	print "QIE card: {0} (crate {1}, slot {2})".format(qid, at.fe_crate, at.fe_slot)
	print ""
	print '(1) Link pattern test:'
	print "BXs read out: {0}".format(100*n_reads)
	if len(error_record.keys()) > 0:
#		print error_record
		print "[!!] Errors:"
		for i_link, errors in error_record.iteritems():
			print "\t* Link {0}: error rate = {1}".format(i_link, errors/float(100*n_reads))
	else:
		print "[OK] There were no errors!"
	print ""
	print '(2) uHTR link test:'
	print "BXs read out: {0}".format(100*n_reads)
	if sum(errdata.values()) > 0:
		print "[!!] Errors:"
		for i_link, errors in errdata.iteritems():
			if errors > 0:
				print "\t* Link {0}: error rate = {1}".format(i_link, errors)
	else:
		print "[OK] There were no errors!"

def create_plots(qie_id):
	th1s = {}
	# For (1):
	h0 = TH1F("link_pattern", "{0}: Link Pattern Errors".format(qie_id), 6, -0.5, 5.5)
	h0.GetXaxis().CenterTitle(1)
	h0.GetXaxis().SetTitle("Link")
	h0.GetYaxis().CenterTitle(1)
	h0.GetYaxis().SetTitle("Link Pattern Error Rate")
	h0.SetLineColor(kRed)
	h0.SetFillColor(kRed)
	th1s["link_pattern"] = h0
	
	# For (2):
	h1 = TH1F("uhtr_error", "{0}: uHTR Link Error Rate".format(qie_id), 6, -0.5, 5.5)
	h1.GetXaxis().CenterTitle(1)
	h1.GetXaxis().SetTitle("Link")
	h1.GetYaxis().CenterTitle(1)
	h1.GetYaxis().SetTitle("uHTR Link Error Rate")
	h1.SetLineColor(kRed)
	h1.SetFillColor(kRed)
	th1s["uhtr_error"] = h1
	
	return th1s

def check_pattern_raw(raw, link_pattern="feed beef"):		# Check the link pattern test data for a single BX of data in a channel.
	if len(raw) == 6:
		string_true = link_pattern
		string = raw[4][1:].lower() + " " + raw[2][1:].lower()		# Chop the leading "0" off and combine into one string.
		counters = [raw[1], raw[3], raw[5]]
		if len(set(counters)) != 1:
			return False,0
		else:
			if string != string_true:
				return False,0
			else:
				counter=int(raw[1],16)
				return True,counter
	else:
		print "ERROR (check_pattern_raw): The raw data had a length of {0}, not 6.".format(len(raw))
		return False,0

def check_pattern(data):		# Check link pattern test data.
	if len(data) == 4:
		errors = 0
		d=data[0]
		nbx = len(d)
		if nbx > 0:
			backcounter=0
			for i_bx in range(nbx):
				result = check_pattern_raw(d[i_bx].raw)
				if not result[0]:
					errors += 1
					backcounter=result[1]
					continue
				if backcounter!=0 and result[1]-backcounter!=1:
					errors += 1
					backcounter=result[1]
					continue
				backcounter=result[1]
		else:
			print "ERROR (check_pattern): The number of bunch crossings recorded for Channel {0} was {1}.".format(ch, nbx)
			return False
		return errors
	else:
		print "ERROR (check_pattern): There wasn't data for all channels in the link."
		return False
# /FUNCTIONS

if __name__ == "__main__":
	main()
