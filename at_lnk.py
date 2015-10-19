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
	at.start()		# Start the acceptance test by printing some basic things.
	
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
	
	# (1) Read link error rates from the uHTR:
	print "(1) Reading link error rates from the uHTR ..."
	errdata = uhtr.parse_err(uhtr.get_raw_err(ts=ts, crate=at.be_crate, slot=at.be_slot))
#	print errdata
#	print '\n >> bad data test:'
	for i_link, value in errdata.iteritems():
#		print 'Link {0}: BadDataRate {1}'.format(i_link, value)
		th1s["uhtr"].Fill(i_link%6, 1)
		th1s["uhtr_error"].Fill(i_link%6, value)
#	print "==========================================="
	# /(1)

	# (2) Verify link pattern test:
	print "(2) Performing a link pattern test ..."
	# Get the teststand ready:
	mode_result = ts.set_mode(mode=1)		# Turn on link pattern test mode.
	if not mode_result:
		print "\tERROR (at_lnk.main): Could not turn link pattern test mode on."
		print "\t[!!] Acceptance test aborted."
		sys.exit()
	
	# Read data out and check for errors:
	error_record = {}
	for n_read in range(n_reads):
		print "\t{0}/{1}: Reading link pattern data ...".format(n_read + 1, n_reads)
		for l, link in enumerate(links):
			if v: print "\t\t==== Link", link.n
			data = link.get_data_spy(n_bx=300)
			n_bx = len(data[0])
			th1s["link"].Fill(l, 1)
			if v:
				for i in range(10):
					print "\t\t{0}".format(data[0][i].raw)
			errors = check(data)
			if errors:
				if errors["pattern"] or errors["counter"]:
					if link.n not in error_record:
						error_record[link.n] = [0, 0]
					error_record[link.n][0] += errors["pattern"]
					error_record[link.n][1] += errors["counter"]
					th1s["link_pattern"].Fill(l, errors["pattern"]/float(n_bx))
					th1s["link_counter"].Fill(l, errors["counter"]/float(n_bx))
			else:
				print "ERROR (at_lnk.main): There's something critically wrong with the raw data being read out."
				at.exit()
	
	# Return the teststand to normal:
#	mode_result = ts.set_mode(mode=0)		# Turn off link pattern test mode.
	if not mode_result:
		print "\tWARNING (at_lnk.main): Could not turn link pattern test mode off."
		print "\t[!!] Acceptance test aborted."
		sys.exit()
		
	# Normalize histograms:
	th1s["link"].Scale(1/float(n_reads))
	th1s["link_pattern"].Scale(1/float(n_reads))
	th1s["link_counter"].Scale(1/float(n_reads))
	# /(2)
	
	
	# Write output:
	## Write to the output ROOT file:
	for key, histogram in th1s.iteritems():
		histogram.Write()
	
	## Save the plots:
	### (2):
	at.canvas.cd(1)
	th1s["link"].Draw()
	th1s["link_pattern"].Draw("same")
	th1s["link_counter"].Draw("same")
	gPad.RedrawAxis()
	gPad.SetLogy(1)
	th1s["link"].SetMaximum(1.0)
	th1s["link"].SetMinimum(1e-12)
	
	### (1):
	at.canvas.cd(2)
	th1s["uhtr"].Draw()
	th1s["uhtr_error"].Draw("same")
	gPad.RedrawAxis()
	gPad.SetLogy(1)
	th1s["uhtr"].SetMaximum(1.0)
	th1s["uhtr"].SetMinimum(1e-12)
	
	## Ask the acceptance test object to save everything:
	at.write()
	
	# Print a summary:
	print "\n====== SUMMARY ============================"
	print "Teststand: {0}".format(ts.name)
	print "QIE card: {0} (crate {1}, slot {2})".format(qid, at.fe_crate, at.fe_slot)
	print ""
	print '(1) uHTR link test:'
	print "BXs read out: {0}".format(100*n_reads)
	if sum(errdata.values()) > 0:
		print "[!!] Errors:"
		for i_link, errors in errdata.iteritems():
			if errors > 0:
				print "\t* Link {0}: error rate = {1}".format(i_link, errors)
	else:
		print "[OK] There were no errors!"
	print ""
	print '(2) Link pattern test:'
	print "BXs read out: {0}".format(100*n_reads)
	if len(error_record.keys()) > 0:
#		print error_record
		print "[!!] Errors:"
		for i_link, errors in error_record.iteritems():
			print "\t* Link {0}: error rate = {1}".format(i_link, list_to_string([e/float(100*n_reads) for e in errors]))
	else:
		print "[OK] There were no errors!"
	print "==========================================="

def create_plots(qie_id):
	th1s = {}
	# For (1):
	## Background:
	h11 = TH1F("link", "{0}: Link Pattern Errors".format(qie_id), 6, -0.5, 5.5)
	h11.GetXaxis().CenterTitle(1)
	h11.GetXaxis().SetTitle("Link")
	h11.GetYaxis().CenterTitle(1)
	h11.GetYaxis().SetTitle("Link Pattern Error Rate")
	h11.SetLineColor(kGreen)
	h11.SetFillColor(kGreen)
	th1s["link"] = h11
	## Pattern errors:
	h12 = TH1F("link_pattern", "", 6, -0.5, 5.5)
	h12.SetLineColor(kRed)
	h12.SetFillColor(kRed)
	th1s["link_pattern"] = h12
	## Counter errors:
	h13 = TH1F("link_counter", "", 6, -0.5, 5.5)
	h13.SetLineColor(kOrange)
	h13.SetFillStyle(0)
	th1s["link_counter"] = h13
	
	# For (2):
	## Background:
	h21 = TH1F("uhtr", "{0}: uHTR Link Error Rate".format(qie_id), 6, -0.5, 5.5)
	h21.GetXaxis().CenterTitle(1)
	h21.GetXaxis().SetTitle("Link")
	h21.GetYaxis().CenterTitle(1)
	h21.GetYaxis().SetTitle("uHTR Link Error Rate")
	h21.SetLineColor(kGreen)
	h21.SetFillColor(kGreen)
	th1s["uhtr"] = h21
	## Errors:
	h22 = TH1F("uhtr_error", "", 6, -0.5, 5.5)
	h22.SetLineColor(kRed)
	h22.SetFillColor(kRed)
	th1s["uhtr_error"] = h22
	
	return th1s

def check_pattern_raw(raw, link_pattern="feed beef"):
	if len(raw) == 6:
		string_true = link_pattern
		string = raw[4][1:].lower() + " " + raw[2][1:].lower()		# Chop the leading "0" off and combine into one string.
		return string == string_true
	else:
		print "ERROR (at_lnk.check_pattern_raw): The raw data had a length of {0}, not 6.".format(len(raw))
		return False

def check_counter_raw(raw):
	if len(raw) == 6:
		counters = [int(raw[1], 16), int(raw[3], 16), int(raw[5], 16)]
		return (list(set(counters))[0], False)[len(set(counters)) != 1]
	else:
		print "ERROR (at_lnk.check_counter_raw): The raw data had a length of {0}, not 6.".format(len(raw))
		return False

def check(data):		# Check link pattern test data.
	errors = {
		"pattern": 0,
		"counter": 0,
	}
	if len(data) == 4:
		d = data[0]
		nbx = len(d)
		if nbx > 0:
			counter = False
			for i_bx in range(nbx):
				result_pattern = check_pattern_raw(d[i_bx].raw)
				result_counter = check_counter_raw(d[i_bx].raw)
				if not result_pattern:
					errors["pattern"] += 1
				if not result_counter:
					errors["counter"] += 1
				else:
					if counter:
						if result_counter != counter + 1:
							errors["counter"] += 1
						counter = result_counter
					else:
						counter = result_counter
			return errors
		else:
			print "ERROR (check_pattern): The number of bunch crossings recorded for Channel {0} was {1}.".format(ch, nbx)
			return False
	else:
		print "ERROR (check_pattern): There wasn't data for all channels in the link."
		return False
# /FUNCTIONS

if __name__ == "__main__":
	main()
