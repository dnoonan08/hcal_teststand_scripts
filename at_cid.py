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
	# Commandline options:
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is \"157\")",
		metavar="STR"
	)
	parser.add_option("-q", "--qie", dest="qie",
#		default="0x9B32C370 0x67000000",
		default="0xAA24DA70 0x8D000000",
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
		help="The number of groups of 100 BXs you want to read per link per phase setting (defualt is 10).",
		metavar="INT"
	)
	(options, args) = parser.parse_args()
	
	# Variables:
	name = options.ts
	v = options.verbose
	if not options.out:
		path = "data/at_results/{0}/at_cid".format(options.qie.replace(" ", "_"))
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/".format(name) + options.out
	n_reads = int(options.n)
	
	# Set up teststand and print basic info about the test:
	ts = teststand(name)
	log = ""
	t_string = time_string()[:-4]
	print "\n> Running the CAPID error rate acceptance test ..."
	
	# Set up basic variables for the test:
	crate, slot = ts.crate_slot_from_qie(qie_id=options.qie)
#	link_dict = ts.uhtr_from_qie(qie_id=options.qie)
	links = []
#	for uhtr_slot, i_links in link_dict.iteritems():
#		for i_link in i_links:
	links = uhtr.get_links_from_map(ts=ts, crate=crate, slot=slot, end="fe")[crate,slot] #, i_link=i_link)
# get_links_from_map(ts=None, crate=None, slot=None, end="be", i_link=None, f="", d="configuration/maps"):
	th1 = create_plots(options.qie)
	print "\tTeststand: {0}".format(ts.name)
	print "\tQIE card: {0} (crate {1}, slot {2})".format(options.qie, crate, slot)
	
	# Run the test:
	error_record = {"bxs": n_reads*100}
	for phase in range(1):		# Loop over possible phase shifts.
		print "> Checking phase {0} ...".format(phase)
		ts.set_clk_phase(crate=crate, slot=slot, phase=phase)
#                print links 
		for link in links:
#                        link.Print()
			result_total = [0 for i in range(4)]
			for i in range(n_reads):
	                        data = link.get_data_spy()
	                        #print data
				result = check_cid_rotating(data)
				for ch, errors in enumerate(result):
#					print "fill {0}: {1} {2}".format(link.qies[ch]-1, phase, errors)
                                        print "ch,errors" , ch, errors
                                        print "link.qies[ch]-1:", link.qies[ch]-1
					th1[link.qies[ch]-1].Fill(phase, errors)
				result_total = [sum(x) for x in zip(result_total, result)]
				if (v): print "\t{0} - Link {1}: {2}".format(i, link.n, result)
#			print result_total
		        print "sum(result_total)",sum(result_total),"result_total:",result_total	
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
		histogram.Scale(1/(100*float(n_reads)))
	
	# Reset the teststand:
	ts.set_clk_phase(crate=crate, slot=slot, phase=0)
	
	# Write output:
	## Write the output ROOT file:
	path += "/" + t_string
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
	gROOT.SetStyle("Plain")
	gROOT.SetBatch()
	gStyle.SetOptStat(0)
	gStyle.SetTitleBorderSize(0)
#	gStyle.SetTitleAlign(21)
	tc = TCanvas("tc", "tc", 2000, 3000)
	tc.SetCanvasSize(2000, 3000)
	tc.Divide(4, 6)
	tc_small = TCanvas("tc_small", "tc_small", 2000, 500)
	tc_small.Divide(4, 1)
	for i, histogram in enumerate(th1):
#		print i
		tc.cd(i + 1)
		histogram.Draw()
		histogram.SetMaximum(1.0)
		histogram.SetMinimum(0.0)
		
		# Deal with small canvas:
		tc_small.cd(i%4 + 1)
		histogram.Draw()
		if (i + 1)%4 == 0:
			n = (i + 1)/4
			tc_small.SaveAs("{0}/{1}_{2}_cid.pdf".format(path, t_string, n))
			tc_small.SaveAs("{0}/{1}_{2}_cid.svg".format(path, t_string, n))
	tc.SaveAs("{0}/{1}_cid.pdf".format(path, t_string))
	tc.SaveAs("{0}/{1}_cid.svg".format(path, t_string))
#	with open("{0}/at_cid.txt".format(path), "w") as out:
#		out.write(log.strip())
	
	# Print a summary:
	print "\n====== SUMMARY ============================"
	print "Teststand: {0}".format(ts.name)
	print "QIE card: {0} (crate {1}, slot {2})".format(options.qie, crate, slot)
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
	
	# Make plots:
	for i in range(24):		# One for each QIE chip on the card
		histogram = TH1F("qie{0}".format(i+1), "{0}: QIE {1}".format(qie_id, i+1), 16, -0.5, 15.5)
		histogram.GetXaxis().CenterTitle(1)
		histogram.GetXaxis().SetTitle("Clock Phase Setting (~1.6 ns)")
		histogram.GetYaxis().CenterTitle(1)
		histogram.GetYaxis().SetTitle("CID Error Rate")
		histogram.GetYaxis().SetTitleOffset(1.3)
		histogram.SetLineColor(kRed)
		histogram.SetFillColor(kRed)
		th1.append(histogram)
	return th1

def check_cid_rotating(data):
	###############################################################
	# Checks if the CIDs are rotating.                            #
	# Input: List of list of datum objects.                       #
	###############################################################
	n_ch = len(data)
	result = [0 for i in range(n_ch)]
	n_bx = 0
	if n_ch > 0:
		n_bx = len(data[0])
	if (n_bx > 0):
		for ch in range(n_ch):
                        
			cid_start = data[ch][0].cid
                        print "ch, cid_start:",ch, cid_start
			for bx, datum in enumerate(data[ch]):
#				if bx < 5:
#					print "{0}: {1}".format(bx, datum.cid)
			        print "bx % 4 :" ,bx % 4
                                print "bx:",bx
                                print "datum.cid:",datum.cid	
				if datum.cid != ((bx % 4) + cid_start) % 4:
                                        print "result[ch]:",result[ch]
					result[ch] += 1
		return result
	else:
		print "ERROR (check_cid_rotating): There were no bunch crosses in the data ..."
		return False
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	main()
# /MAIN
