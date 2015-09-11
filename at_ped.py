from hcal_teststand.hcal_teststand import *
import hcal_teststand.uhtr
import numpy
from optparse import OptionParser
import hcal_teststand.qie
from hcal_teststand.utilities import time_string
from ROOT import *
from array import array
import os
from math import sqrt
# one big (?) issue with this whole setup, that maybe is 
# solved somehow, is that we want to be able to run tests 
# for individual QIE cards.  If there are multiple QIE 
# cards per uHTR we will also need to figure out which 
# channel of the uHTR connects to which QIE card.  


if __name__ == "__main__":
	xs=array('d')
	ys=array('d')
	xers=array('d')
	yers=array('d')
	parser=OptionParser()
	parser.add_option('-t','--teststand',dest='name',default='904',help="The name of the teststand you want to use (default is \"904\").")
	parser.add_option('-q','--qieid',dest='qieid',default='0x9B32C370 0x67000000',help="The ID of the QIE card from which we read the pedestal.")
	parser.add_option('-o','--output',dest='out',default='data/ts_904/plots',help="The directory in which the output file will be saved.")
	(options, args) = parser.parse_args()
	ts = teststand(options.name)
	slotlink=ts.uhtr_from_qie(qie_id=options.qieid)
	if slotlink=={}:
		print 'ERROR: No such QIE ID'
		exit()
	slot=slotlink.keys()[0]
	links=slotlink[slot]
	print 'slot:',slot
	d = time_string()
	fdnm=options.out+'/'+d.split('_')[0]
	if not os.path.exists(fdnm):
		os.makedirs(fdnm)
	print "pedestalTest_{0}.root".format(d)
	uhtr.get_histo(ts,50,slot,1000,1,fdnm+"/pedestalTest_{0}.root".format(d))
	inputFile = TFile(fdnm+"/pedestalTest_{0}.root".format(d),"READ")
	gStyle.SetFillColor(0)
	gStyle.SetOptStat(111111)
        gStyle.SetOptTitle(0)
	can = TCanvas("can","can",800,600)
	can1=TCanvas('can1','can1',1200,400)
	can2 = TCanvas("can2","can2",800,600)
	can3 = TCanvas("can3","can3",800,600)
	can1.Divide(3,1)
        can2.Divide(2,2)
	means=TH1F('mean','mean',20,0,20)
	rmss=TH1F('rms','rms',24,0,6)
	CapID0=TH1F('CapID0','CapID0',64,0,63)
	CapID1=TH1F('CapID1','CapID1',64,0,63)
	CapID2=TH1F('CapID2','CapID2',64,0,63)
	CapID3=TH1F('CapID3','CapID3',64,0,63)
	print "plotting histograms..."
	for link  in links : 
	#	if link.n is -1: 
	#		print "---------------------------"
	#		print 'BAD LINK'
	#		continue
		print "---------------------------"
		print 'link:',link
		print "---------------------------"
		h = [ ]
		leg = TLegend(0.4773869,0.9405594,0.5552764,0.9755245)
		leg.SetHeader("link{0}".format(link))
		for i in range(4):
			temp = inputFile.Get("h{0}".format(4*link+i) )
			#temp.GetXaxis().SetRangeUser(0,20)
			temp.GetYaxis().SetTitle("Events")
			temp.GetXaxis().SetTitle("ADC")
			temp.SetLineColor(1+i)
			temp.GetYaxis().SetTitleOffset(1.4)
			temp.GetXaxis().SetTitleOffset(1.1)
			temp.GetYaxis().SetTitleSize(0.04)
			temp.GetXaxis().SetTitleSize(0.04)
			temp.GetYaxis().SetLabelSize(0.04)
			temp.GetYaxis().SetLabelOffset(0.02)
			temp.GetXaxis().SetLabelOffset(0.01)
			temp.GetXaxis().SetLabelSize(0.04)
			h.append(temp)
			for j in range(1,65):
				CapID0.Fill(j-1,temp.GetBinContent(j))
				means.Fill(CapID0.GetMean())
                        	rmss.Fill(CapID0.GetRMS())
			for k in range(65,129):
                                CapID1.Fill(k-65,temp.GetBinContent(k))
			    	means.Fill(CapID1.GetMean())
                       		rmss.Fill(CapID1.GetRMS())
			for l in range(129,193):
                                CapID2.Fill(l-129,temp.GetBinContent(l))
			    	means.Fill(CapID2.GetMean())
                        	rmss.Fill(CapID2.GetRMS())
			for m in range(193,257):
                                CapID3.Fill(m-193,temp.GetBinContent(m))
				means.Fill(CapID3.GetMean())
                        	rmss.Fill(CapID3.GetRMS())
			xs.append(4*link+i)
			ys.append((CapID0.GetMean()+CapID1.GetMean()+CapID2.GetMean()+CapID3.GetMean())/4)
			xers.append(0)
			yers.append(sqrt((CapID0.GetRMS()**2+CapID1.GetRMS()**2+CapID2.GetRMS()**2+CapID3.GetRMS()**2)/4))
			can2.cd(1).SetLogy()
			CapID0.Draw()
			can2.cd(2).SetLogy()
			CapID1.Draw()
			can2.cd(3).SetLogy()
			CapID2.Draw()
			can2.cd(4).SetLogy()
			CapID3.Draw()
			can2.SaveAs(fdnm+"/CapID_{0}_link{1}_Channel{2}.png".format(d,link,i))	
		        CapID0.Reset()
			CapID1.Reset()
			CapID2.Reset()
			CapID3.Reset()	
			can3.cd()
			can3.SetLogy()
			temp.Draw()
			can3.SaveAs(fdnm+"/h{0}.png".format(4*link+i))
			can.cd()
	                can.SetLeftMargin(0.1193467)
   			can.SetRightMargin(0.06030151)
   			can.SetTopMargin(0.07867133)
   			can.SetBottomMargin(0.1398601)
			leg.SetMargin(0.2)
           	 	leg.SetFillColor(kWhite)
            		leg.SetBorderSize(0)
            		leg.SetTextSize(0.035)
			if len(h) == 1 :
				h[-1].Draw()
			else :
				h[-1].Draw("SAME")
#			temp.GetXaxis().SetRangeUser(0,250)
			leg.Draw("SAME")	 
		can.Print(fdnm+"/pedestalTest_{0}_link{1}.png".format(d,link))
	gre=TGraphErrors(len(xs),xs,ys,xers,yers)
	can1.cd(1)
	means.SetTitle('pedestal mean distribution;mean;channels')
	means.Draw()
	can1.cd(2)
	rmss.SetTitle('pedestal RMS distribution;RMS;channels')
	rmss.Draw()
	can1.cd(3)
	gre.SetTitle('pedestal vs channel;channel;pedestal')
	gre.SetMarkerStyle(8)
	gre.Draw('ap')
	can1.Print(fdnm+'/ped_{0}.png'.format(d))
