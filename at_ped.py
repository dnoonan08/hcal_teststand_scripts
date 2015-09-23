####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: [description]                                       #
####################################################################

# IMPORTS:
from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
#import os
from ROOT import *
import numpy
from math import sqrt
from array import array
# /IMPORTS

# CLASSES:
# /CLASSES

# VARIABLES:
xs_cid0 ,  ys_cid0 ,  xers_cid0 , yers_cid0 , xs_cid1  , ys_cid1 , xers_cid1 , yers_cid1 , xs_cid2 ,  ys_cid2 ,  xers_cid2 , yers_cid2 , xs_cid3 , ys_cid3 , xers_cid3 , yers_cid3 =array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d')
# /VARIABLES

# FUNCTIONS:
def fill(temp, th1s, qie, cid):
	plot = th1s[qie, cid]
	#print 'Filling %s %s %s' % (qie, cid, plot)
	for i in range(1,65):
		plot.Fill(i-1,temp.GetBinContent(i+cid*64))
		#print 'Integral value of the histogram %s %s %s' % (qie, cid, plot.Integral())
		#print 'Mean value of the histogram %s %s %s:' % (qie, cid, plot.GetMean())

if __name__ == "__main__":
	# Make an acceptance test object:
	at = tests.acceptance(name="ped")		# Create an acceptance test.
	at.start()		# Start the acceptance test by printing some basic things.
	
	# Variables:
	ts = at.ts
	be_crate = at.be_crate
	be_slot = at.be_slot
	links = [l.n for l in at.links]
	
	# Read pedestal information from the uHTR:
	f_in = at.path + "/uhtr_histograms.root"
	uhtr.get_histo(ts, be_crate, be_slot, 1000, 1, f_in)
	inputFile = TFile(f_in, "READ")
	
	# Analyze the data:
#	can = TCanvas("Histograms from the uHTR tool","Histograms from the uHTR tool",800,600)
#	can1 = TCanvas("CID","CID",800,600)
#	can2 = TCanvas("QIE","QIE",800,600)
	at.canvas.SetCanvasSize(1280, 460)
	at.canvas.Divide(3, 1)
#	at.canvas.cd(1)
#	h0 = TH1F("test", "TEST", 10, 0, 10)
#	h0.Draw()
	
	means = TH1F('mean','mean',20,0,20)
	rmss = TH1F('rms','rms',24,0,6)
	th1s={}
	
	for link  in links:
		print "---------------------------"
		print 'link:', link
		print "---------------------------"
		h = []
		leg = TLegend(0.4773869,0.9405594,0.5552764,0.9755245)
		leg.SetHeader("link{0}".format(link))
		leg.SetTextSize(0.04)
		leg1 = TLegend(0.8168145,0.8070673,0.9943974,0.9889456)
		leg1.SetFillColor(0)
		leg1.SetBorderSize(1)
		for ch, i_qie in  enumerate(range(4*(link%6)+1,4*(link%6)+5)):
			temp = inputFile.Get("h{0}".format(4*link+ch))
			temp.GetYaxis().SetTitle("Events")
			temp.GetXaxis().SetTitle("ADC")
			temp.SetLineColor(1+ch)
			temp.GetYaxis().SetTitleOffset(1.4)
			temp.GetXaxis().SetTitleOffset(1.1)
			temp.GetYaxis().SetTitleSize(0.04)
			temp.GetXaxis().SetTitleSize(0.04)
			temp.GetYaxis().SetLabelSize(0.04)
			temp.GetYaxis().SetLabelOffset(0.02)
			temp.GetXaxis().SetLabelOffset(0.01)
			temp.GetXaxis().SetLabelSize(0.04)
			h.append(temp)
#			can.cd()
#			can.SetLogy()
#			temp.Draw()
			at.out.WriteTObject(temp)
#			can.SaveAs(fdnm+"/h{0}_{1}.png".format(4*link+ch,d))
			for i_cid in range(4):
				name = 'QIE{0}_CapID{1}'.format(i_qie,i_cid)
				th1s[i_qie,i_cid]=TH1F(name,name,64,0,63)
				fill(temp, th1s, i_qie, i_cid)
#				can1.cd()
#				can1.SetLogy()
#				th1s[i_qie,i_cid].Draw()
				if i_cid == 0 :
					xs_cid0.append(((i_qie-1)*4+i_cid)+1) 
					ys_cid0.append(th1s[i_qie,i_cid].GetMean())
					xers_cid0.append(0)
					yers_cid0.append(th1s[i_qie,i_cid].GetRMS())
				if i_cid == 1 :
					xs_cid1.append(((i_qie-1)*4+i_cid)+1) 
					ys_cid1.append(th1s[i_qie,i_cid].GetMean())
					xers_cid1.append(0)
					yers_cid1.append(th1s[i_qie,i_cid].GetRMS())
				if i_cid == 2 :
					xs_cid2.append(((i_qie-1)*4+i_cid)+1) 
					ys_cid2.append(th1s[i_qie,i_cid].GetMean())
					xers_cid2.append(0)
					yers_cid2.append(th1s[i_qie,i_cid].GetRMS())
				if i_cid == 3 :
					xs_cid3.append(((i_qie-1)*4+i_cid)+1) 
					ys_cid3.append(th1s[i_qie,i_cid].GetMean())
					xers_cid3.append(0)
					yers_cid3.append(th1s[i_qie,i_cid].GetRMS())
			        means.Fill(th1s[i_qie,i_cid].GetMean())
			        rmss.Fill(th1s[i_qie,i_cid].GetRMS())
#				can1.SaveAs(fdnm+"/link{0}_qie{1}_CapID{2}_{3}.png".format(link,i_qie,i_cid,d))		
#			can2.cd()
#			if len(h) == 1 :
#				h[-1].Draw()
#			else :
#				h[-1].Draw("SAME")
#			leg.Draw("SAME")
#		can2.Print(fdnm+"/pedestalTest_{0}_link{1}.png".format(d,link))
	for key, plot in th1s.iteritems():
       		at.out.WriteTObject(plot)
	# Write and Draw Mean, RMS, Pedestal vs Channel distribution 
	mg = TMultiGraph("PedestalvsChannel","PedestalvsChannel");
	mg.SetTitle("PedestalvsChannel;number of cap ID;mean");
	gre_cid0=TGraphErrors(len(xs_cid0),xs_cid0,ys_cid0,xers_cid0,yers_cid0)
	gre_cid1=TGraphErrors(len(xs_cid1),xs_cid1,ys_cid1,xers_cid1,yers_cid1)
	gre_cid2=TGraphErrors(len(xs_cid2),xs_cid2,ys_cid2,xers_cid2,yers_cid2)
	gre_cid3=TGraphErrors(len(xs_cid3),xs_cid3,ys_cid3,xers_cid3,yers_cid3)
	at.canvas.cd(1)
	means.SetTitle('pedestal mean distribution;mean;channels')
	means.Draw()
	at.out.WriteTObject(means)
	at.canvas.cd(2)
	rmss.SetTitle('pedestal RMS distribution;RMS;channels')
	rmss.Draw()
	at.out.WriteTObject(rmss)
	at.canvas.cd(3)
	leg1.AddEntry(gre_cid0, "CapID0","p")
	leg1.AddEntry(gre_cid1, "CapID1","p")
	leg1.AddEntry(gre_cid2, "CapID2","p")
	leg1.AddEntry(gre_cid3, "CapID3","p")
	gre_cid0.SetMarkerStyle(8)
	gre_cid0.SetMarkerColor(1)
	gre_cid1.SetMarkerStyle(8)
	gre_cid1.SetMarkerColor(2)
	gre_cid2.SetMarkerStyle(8)
	gre_cid2.SetMarkerColor(3)
	gre_cid3.SetMarkerStyle(8)
	gre_cid3.SetMarkerColor(4)
	mg.Add(gre_cid0)
	mg.Add(gre_cid1)
	mg.Add(gre_cid2)
	mg.Add(gre_cid3)
	mg.Draw('ap')
	leg1.Draw("SAME")
	at.out.WriteTObject(mg)
	
#	# Save output:
	at.write()		# Save the "at.canvas" canvas and close the "at.out" ROOT file.

