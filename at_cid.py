####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: This test checks to make sure the capacitor IDs     #
# (CIDs) are rotating correctly on each QIE, for each phase shift  #
# setting.                                                         #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
import os
from optparse import OptionParser
from ROOT import *

# CLASSES:
# /CLASSES

# FUNCTIONS:
def main():
	# Make an acceptance test object:
	at = tests.acceptance(name="cid")		# Create an acceptance test.
	at.start()		# Start the acceptance test by printing some basic things.
	
	# Variables and simple set up:
	ts = at.ts
	qid = at.qid
	links = at.links
	v = at.verbose
	th1, th2 = create_plots(qid)
	n_reads = at.n
	error_record = {"bxs": n_reads*100}
	
	# Run the test:
	for phase in range(16):		# Loop over possible phase shifts.
		print "Checking QIE clock phase setting {0}/15 ...".format(phase)
		ts.set_clk_phase(phase=phase, script=True)
		for link in links:
#		for link in [links[3]]:
#			print "======= LINK", link.n
			result_total = [0 for i in range(4)]		# Prepare for results per channel.
			for i in range(n_reads):
				data = link.get_data_spy(n_bx=300)
				if data:
					n_bx = len(data[0])
					for ch in range(4):
						th1[link.qies[ch]-1].Fill(phase, 1)
					result = check_cid_rotating(data)
#					print result
					if result:
						for ch, errors in enumerate(result):
							th2[link.qies[ch]-1].Fill(phase, errors/float(n_bx))		# Normalize the histograms (making a "rate")
						result_total = [sum(x) for x in zip(result_total, result)]
						if (v): print "\t{0} - Link {1}: {2}".format(i, link.n, result)
					else:
						print "ERROR (at_cid): Something ungood happened inside the check_cid_rotating function."
						at.exit()
				else:
					print "ERROR (at_cid): Acquiring SPY data from Link {0} failed!".format(link.n)
					at.exit()
#			print result_total
#			print "sum(result_total)",sum(result_total),"result_total:",result_total	
			# Record errors:
			if sum(result_total) != 0:
				if link.n not in error_record:
					error_record[link.n] = {}
				for ch, count in enumerate(result_total):
					if count != 0:
						if ch not in error_record[link.n]:
							error_record[link.n][ch] = [0 for i in range(16)]
						error_record[link.n][ch][phase] = count
	
	# Normalize histograms:
	for histogram in th1:
		histogram.Scale(1/float(n_reads))
	for histogram in th2:
		histogram.Scale(1/float(n_reads))
	
	# Reset the teststand:
	ts.set_clk_phase(phase=0)
	
	# Write output:
	for histogram in th1:
		histogram.Write()		# This is written to the TFile at.out
	for histogram in th2:
		histogram.Write()		# This is written to the TFile at.out
	
	## Save the plots in a PDF (and PNG):
	at.canvas.SetCanvasSize(2000, 3000)
	at.canvas.Divide(4, 6)
	for i, histogram in enumerate(th1):
#		print i
		at.canvas.cd(i + 1)
		histogram.Draw()
		histogram.SetMaximum(1.0)
#		histogram.SetMinimum(0.0)
	for i, histogram in enumerate(th2):
#		print i
		at.canvas.cd(i + 1)
		histogram.Draw("same")
		gPad.RedrawAxis()
		gPad.SetLogy(1)
	at.write()
	
	# Print a summary:
	print "\n====== SUMMARY ============================"
	print "Teststand: {0}".format(ts.name)
	print "QIE card: {0} (FE Crate {1}, Slot {2})".format(qid, at.fe_crate, at.fe_slot)
	print "BXs/phase setting: {0}".format(100*n_reads)
	if len(error_record.keys()) > 1:
#		print error_record
		print "[!!] Errors: (indexed by phase setting)"
		for i_link in [i for i in error_record.keys() if isinstance(i, int)]:
			for i_ch, counts in error_record[i_link].iteritems():
				print "\t* Link {0}, Channel {1}: error rates = {2}".format(i_link, i_ch, list_to_string([i/float(error_record["bxs"]) for i in counts]))
	else:
		print "[OK] There were no errors!"
	print "==========================================="

def create_plots(qie_id):
	###############################################################
	# Makes empty plots that will be filled with error data.      #
	###############################################################
	# Variables:
	th1 = []
	th2 = []
	
	# Make plots:
	gStyle.SetOptStat(0)
	for i in range(24):		# One for each QIE chip on the card
		histogram = TH1F("qie{0}".format(i+1), "{0}: QIE {1}".format(qie_id, i+1), 16, -0.5, 15.5)
		histogram.GetXaxis().CenterTitle(1)
		histogram.GetXaxis().SetTitle("Clock Phase Setting (~1.6 ns)")
		histogram.GetYaxis().CenterTitle(1)
		histogram.GetYaxis().SetTitle("CID Error Rate")
		histogram.GetYaxis().SetTitleOffset(1.3)
		histogram.SetLineColor(kGreen)
		histogram.SetFillColor(kGreen)
		th1.append(histogram)
	for i in range(24):		# One for each QIE chip on the card
		histogram = TH1F("qie{0}_error".format(i+1), "{0}: QIE {1}".format(qie_id, i+1), 16, -0.5, 15.5)
		histogram.SetLineColor(kRed)
		histogram.SetFillColor(kRed)
		th2.append(histogram)
	return (th1, th2)

def check_cid_rotating(data):
	###############################################################
	# Checks if the CIDs are rotating.                            #
	# Input: List of list of datum objects.                       #
	###############################################################
#	for d in data[0]:
#		d.cid = -1
	n_ch = len(data)
	result = [0 for i in range(n_ch)]
	n_bx = 0
	if n_ch > 0:
		n_bx = len(data[0])
	else:
		print "ERROR (at_cid.check_cid_rotating): The data is formatted oddly:"
		print data
		return False
	if n_bx > 0:
		for ch in range(n_ch):
			cid_start = data[ch][0].cid
			counter = 0
			while cid_start == -1:
				counter += 1
				result[ch] += 1
				if counter < n_bx:
					cid_start = data[ch][counter].cid
				else:
					cid_start = -2
#			print "ch, cid_start:",ch, cid_start
			data[ch][counter:]
			for bx, datum in enumerate(data[ch][counter:]):
#				print "{0}: {1}".format(bx, datum.cid)
				if datum.cid != ((bx % 4) + cid_start) % 4:
					result[ch] += 1
		return result
	else:
		print "ERROR (at_cid.check_cid_rotating): There were no bunch crosses in the data ..."
		return False
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	main()
# /MAIN
