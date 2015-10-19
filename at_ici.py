####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: ICI                                                 #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
import os
from optparse import OptionParser
from ROOT import *
from array import array
import numpy

# CLASSES:
# /CLASSES

# FUNCTIONS:
def main():
	# Make an acceptance test object:
	at = tests.acceptance(name="ici")		# Create an acceptance test.
	at.start(False)		# Start the acceptance test by printing some basic things.
	
	# Variables and simple set up:
	v = at.verbose
	ts = at.ts
	if v: ts.Print()
	qid = at.qid
	links = at.links
#	print links
	n_events = at.n
	th2s = create_plots()
#	data = {}		# To be indexed by QIE.
	
	# Set up:
	print "Setting CI mode and TDC threshold ..."
	ci_result = ts.set_ci(enable=True, script=False)		# Turn on internal charge-injection mode.
	threshold_result = ts.set_tdc_threshold(threshold=1, script=True, verbose=False)		# Set the TDC threshold to its lowest value.
	
	# Do the test:
	if ci_result:
		for phase in range(16):
			phase_result = ts.set_clk_phase(phase=phase, script=True)		# Set the phase for all QIEs.
			if phase_result:
				print "({0}/15) Getting data for Phase Setting {0} ...".format(phase)
				for link in links:
					if v: print "==============="
					if v: print "Link {0}:".format(link.n)
					if v: print "==============="
					uhtr_out = uhtr.get_triggered_data(ts=ts, crate=at.be_crate, slot=at.be_slot, i_link=link.n, n_events=n_events, f="at_ici_{0}_{1}".format(phase, link.n), script=True)
					if uhtr_out:
#						for ch in range(4):
#							data[link.qies[ch], phase] = []
						raw = open("at_ici_{0}_{1}.txt".format(phase, link.n), "r").read()
						events = uhtr.parse_l1a(raw=raw)
						if link.n == 15:
							for ch in range(4):
								print [events[0][i][ch].tdc for i in range(15)]
								print [events[0][i][ch].adc for i in range(15)]
								print [events[0][i][ch].cid for i in range(15)]
								print [events[0][i][ch].raw for i in range(15)]
								print "\n"
						data = parse_data(events=events, link=link)
						fill_plots(th2s, data, phase)
#						print data
#						fill_plots(mg=mg, th1=th1, th2=th2, link=link, events=events, phase=phase)
						if v:
							for event in events:
								for ch in range(4):
									print "Channel {0}:".format(ch)
									for i_bx, ds in enumerate(event):
										print ds[ch], ds[ch].raw
					else:
						print "ERROR (at_ici.main): Failed to get triggered data. If this is error is due to a timeout, you might need to turn the trigger on."
		#				at.exit()
			else:
				print "ERROR (at_ici.main): Failed to set the QIE clock phases to {0}.".format(phase)
				at.exit()
	else:
		print "ERROR (at_ici.main): Failed to set IC mode."
		at.exit()
	
	# Restore defaults:
	phase_result = ts.set_clk_phase(phase=0, script=True)		# Set the phase for all QIEs.
	
	# Deal with the data:
#	print data
#	for i in range(1, 25):
#		print i, [d.tdc_le for d in data[i,0]]
#	mg = make_graphs(data)
#	th1 = make_histograms(data)
	
	# Write output:
	at.canvas.SetCanvasSize(500, 750)
#	at.canvas.Divide(6)
	at.canvas.Divide(4, 6)
	for i_qie, th2 in th2s.iteritems():
		gStyle.SetOptStat(0)
		at.canvas.cd(i_qie)
		th2.Draw("COLZ")
		th2.Write()
#	for i_qie in range(1, 25):
#		tg[i_qie].Draw("AP")
#		tg[i_qie].Write()
#		for phase in range(16):
#			th1[i_qie, phase].Write()
#		at.out.WriteTObject(tg[i_qie])
#	for i_qie in range(1, 25):
#		gStyle.SetOptStat(0)
#		at.canvas.cd(i_qie)
##		mg[i_qie].Draw("AP")
#		th2[i_qie].Draw("COLZ")
#		mg[i_qie].Write()
#		th2[i_qie].Write()
##	format_graphs(mg)
#	for h in th1.values():
#		h.Write()
	at.write()


def create_plots():
	# Variables:
#	mg = {}		# One for each QIE
#	th1 = {}
	th2s = {}
	
	# Set up:
	for i_qie in range(1, 25):
#		mg[i_qie] = TMultiGraph()
#		mg[i_qie].SetName("mg{0}".format(i_qie))
		th2s[i_qie] = TH2F("h{0}".format(i_qie), "", 15, 0, 15, 64, 0, 64)
#		for phase in range(16):
#			for i_bx in range(15):
#				th1[i_qie, phase, i_bx] = TH1F("QIE{0}_P{1}_BX{2}".format(i_qie, phase, i_bx), "", 64, 0, 64)
	return th2s

def parse_data(events=None, link=None):
	data = {}
	for ch in range(4):
		i_qie = link.qies[ch]
		tdcs = [[bx[ch].tdc for bx in event] for event in events]
#		print tdcs
		tdcs = [[t for t in tdc if t != 63] for tdc in tdcs]
		tdcs = [tdc + [63]*(2-len(tdc)) for tdc in tdcs]
#		print i_qie, tdcs
		data[i_qie] = tdcs
	return data

def fill_plots(th2s, data, phase):
	for i_qie, events in data.iteritems():
		for event in events:
			for value in event:
				th2s[i_qie].Fill(phase, value)

def format_graphs(mg):
	# Set up:
	for i_qie, m in mg.iteritems():
		m.GetYaxis().SetTitle("TDC")
	return True

#def fill_plots(mg=None, th1=None, th2=None, link=None, events=None, phase=None, color=kBlack):
#	for ch in range(4):
#		# Variables:
#		i_qie = link.qies[ch]
#		n_bx = len(events[0])
#		
#		# Fill graphs:
#		x = array("d")
#		x_e = array("d")
#		y = array("d")
#		y_e = array("d")
#		for i_bx in range(n_bx):
#			tdcs = [event[i_bx][ch].tdc_le for event in events]
##			tdcs = [0 if t == 62 else t for t in tdcs]
#			if 61 in tdcs:
#				color = kRed
#			x.append(i_bx)
#			x_e.append(0)
#			y.append(numpy.mean(tdcs))
#			y_e.append(numpy.std(tdcs))
##			if 61 in tdcs:
##				color = kRed
##				w = 60
##			elif numpy.mean(tdcs) < 50:
##				w = numpy.mean(tdcs)/2
##			elif numpy.mean(tdcs) >= 50 and numpy.mean(tdcs) < 62:
##				w = 30
##			elif numpy.mean(tdcs) == 62:
##				w = 40
##			elif numpy.mean(tdcs) == 63:
##				w = 50
##			else:
##				w = 30
#			th2[i_qie].Fill(i_bx, numpy.mean(tdcs))
#		if len([t for t in y if t < 50]) > 1 and color != kRed:
#			color = kOrange
#		tg = TGraphErrors(len(x), x, y, x_e, y_e)
#		tg.SetMarkerColor(color)
#		tg.SetLineColor(color)
#		mg[i_qie].Add(tg)
#		
#		# Fill histograms
#		for i_bx in range(n_bx):
#			for event in events:
#				th1[i_qie, phase, i_bx].Fill(event[i_bx][ch].tdc_le)
#	return True

def make_graphs(data):
	# Variables:
	colors = [kBlack, kRed, kBlue, kSpring]
	tg = {}		# Indexed by the QIE number and phase
	mg = []		# Groups of 4 QIE graphs
	
	# Set up:
	for i in range(6):
		mg_temp = TMultiGraph()
		mg_temp.SetName("mg{0}".format(i))
		mg.append(mg_temp)
	
	# Make graphs and fill multigraphs:
	for i_qie in range(1, 25):
		x = array("d")
		x_e = array("d")
		y = array("d")
		y_e = array("d")
		for phase in range(16):
			x.append(phase)
			x_e.append(0)
			tdcs = [d.tdc_le for d in data[i_qie, phase] if d.tdc_le < 50]
			if not tdcs:
				tdcs = [60]
			y.append(numpy.mean(tdcs))
			y_e.append(numpy.std(tdcs))
		tg[i_qie] = TGraphErrors(len(x), x, y, x_e, y_e)
		tg[i_qie].SetName("tg{0}".format(i_qie))
		tg[i_qie].SetLineColor(colors[(i_qie-1)%4])
		mg[(i_qie-1)/6].Add(tg[i_qie])
	return mg

def make_histograms(data):
	th1 = {}
	for i_qie in range(1, 25):
		for phase in range(16):
			tdcs = [d.tdc_le for d in data[i_qie, phase]]
			th1[i_qie, phase] = TH1F("h{0}_{1}".format(i_qie, phase), "", 64, 0, 64)
			for tdc in tdcs:
				th1[i_qie, phase].Fill(tdc)
	return th1
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	main()
# /MAIN
