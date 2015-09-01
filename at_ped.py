from hcal_teststand.hcal_teststand import *
import hcal_teststand.uhtr
import numpy
from optparse import OptionParser
import hcal_teststand.qie
from hcal_teststand.utilities import time_string
from ROOT import *
from array import array
import os
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
	uhtr.get_histo(ts,50,slot,1000,0,fdnm+"/pedestalTest_{0}.root".format(d))
	inputFile = TFile(fdnm+"/pedestalTest_{0}.root".format(d),"READ")
	gStyle.SetFillColor(0)
	can = TCanvas("can","can",500,500)
	can1=TCanvas('can1','can1',1200,400)
	can1.Divide(3,1)
	means=TH1F('mean','mean',20,0,10)
	rmss=TH1F('rms','rms',18,0,6)
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
		can.cd()
		for i in range(4):
			temp = inputFile.Get("h{0}".format(4*link+i) )
			temp.GetXaxis().SetRangeUser(0,20)
			temp.GetYaxis().SetTitle("Events")
			temp.GetXaxis().SetTitle("ADC")
			temp.SetLineColor(1+i)
			#temp.SetLineStyle(link)
			h.append(temp)
			if len(h) == 1 :
				h[-1].Draw()
			else :
				h[-1].Draw("SAME")
#			temp.GetXaxis().SetRangeUser(0,250)
			means.Fill(temp.GetMean())
			rmss.Fill(temp.GetRMS())
			xs.append(4*link+i)
			ys.append(temp.GetMean())
			xers.append(0)
			yers.append(temp.GetRMS())
		can.SaveAs(fdnm+"/pedestalTest_{0}_link{1}.png".format(d,link))
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
