####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: This test checks to make the capacitor IDs (CIDs)   #
# are rotating correctly on each QIE, for each phase shift         #
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
def create_plots(qie_id):
	th1 = []
	for i in range(24):
		histogram = TH1F("qie{0}".format(i+1), "{0}: QIE {1}".format(qie_id, i+1), 16, -0.5, 15.5)
		histogram.GetXaxis().CenterTitle(1)
		histogram.GetXaxis().SetTitle("Clock Phase Setting (~1.6 ns)")
		histogram.GetYaxis().CenterTitle(1)
		histogram.GetYaxis().SetTitle("CID Error Rate")
		histogram.SetLineColor(kRed)
		histogram.SetFillColor(kRed)
		th1.append(histogram)
	return th1

def check_cid_rotating(data):		# Check if the CIDs are rotating.
	n_ch = len(data)
	result = [0 for i in range(n_ch)]
	n_bx = 0
	if n_ch > 0:
		n_bx = len(data[0])
	if (n_bx > 0):
		for ch in range(n_ch):
			cid_start = data[ch][0].cid
			for bx, datum in enumerate(data[ch]):
#				if bx < 5:
#					print "{0}: {1}".format(bx, datum.cid)
				if datum.cid != ((bx % 4) + cid_start) % 4:
					result[ch] += 1
		return result
	else:
		print "ERROR (check_cid_rotating): There were no bunch crosses in the data ..."
		return False
# /FUNCTIONS

# MAIN:
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
	(options, args) = parser.parse_args()
	name = options.ts
	v = options.verbose
	if not options.out:
		path = "data/ts_{0}/at_results/at_cid".format(name)
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/ts_{0}/".format(name) + options.out
	
	# Set up teststand and print basic info about the test:
	ts = teststand(name)
	log = ""
	t_string = time_string()[:-4]
	print "\n> Running acceptance test CID ..."
	
	# Set up basic variables for the test:
	n_reads = 5
	t_string = time_string()[:-4]
	crate, slot = ts.crate_slot_from_qie(qie_id=options.qie)
	link_dict = ts.uhtr_from_qie(qie_id=options.qie)
	links = []
	for uhtr_slot, i_links in link_dict.iteritems():
		for i_link in i_links:
			links.append(uhtr.get_link_from_map(ts=ts, uhtr_slot=uhtr_slot, i_link=i_link))
	th1 = create_plots(options.qie)
	print "\tTeststand: {0}".format(ts.name)
	print "\tQIE card: {0} (crate {1}, slot {2})".format(options.qie, crate, slot)
	
	# Run the test:
	for phase in range(16):		# Loop over possible phase shifts.
		print "> Checking phase {0} ...".format(phase)
		qie.set_clk_phase_all(ts, crate, slot, phase)
		for link in links:
			for i in range(n_reads):
				data = link.get_data_spy()
				result = check_cid_rotating(data)
				for ch, errors in enumerate(result):
#					print "fill {0}: {1} {2}".format(link.qies[ch]-1, phase, errors)
					th1[link.qies[ch]-1].Fill(phase, errors)
				print "\t{0} - Link {1}: {2}".format(i, link.n, result)
	for histogram in th1:
		histogram.Scale(1/(100*float(n_reads)))
	qie.set_clk_phase_all(ts, crate, slot, 0)
	
	# Write output:
	## Write the output ROOT file:
	file_name = "{0}/{1}_cid.root".format(path, t_string)
	print "> Saving histograms to {0} ...".format(file_name)
	if not os.path.exists(path):
		os.makedirs(path)
	if os.path.exists(file_name):
		tf = TFile(file_name, "RECREATE")
	else:
		tf = TFile(file_name, "NEW")
	for histogram in th1:
		histogram.Write()
	tf.Close()
	
	## Save the plots in a PDF (and SVG):
	gROOT.SetBatch()
	tc = TCanvas("tc", "tc", 2000, 3000)
	tc.SetCanvasSize(2000, 3000)
	tc.Divide(4, 6)
	for i, histogram in enumerate(th1):
		print i
		tc.cd(i + 1)
		histogram.Draw()
		histogram.SetMaximum(1.0)
		histogram.SetMinimum(0.0)
	tc.SaveAs("{0}/{1}_cid.pdf".format(path, t_string))
	tc.SaveAs("{0}/{1}_cid.svg".format(path, t_string))
#	with open("{0}/at_cid.txt".format(path), "w") as out:
#		out.write(log.strip())
# /MAIN
