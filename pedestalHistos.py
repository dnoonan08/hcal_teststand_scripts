from hcal_teststand.hcal_teststand import *
import hcal_teststand.uhtr
import numpy
import sys
import hcal_teststand.qie
from hcal_teststand.utilities import time_string
from ROOT import *
from array import array
# one big (?) issue with this whole setup, that maybe is 
# solved somehow, is that we want to be able to run tests 
# for individual QIE cards.  If there are multiple QIE 
# cards per uHTR we will also need to figure out which 
# channel of the uHTR connects to which QIE card.  
xs=array('d')
ys=array('d')
xers=array('d')
yers=array('d')

if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "bhm"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "bhm"
	ts = teststand(name)

	#ts.set_ped_all(6)
	#set_ped(crate_port, 3, 31)
	links = uhtr.get_links(ts,11)
	#for link in links : 
	#        link.Print()

	d = time_string()
	print "pedestalTest_{0}.root".format(d)
	uhtr.get_histo(ts,11,1000,0,"pedestalTest_{0}.root".format(d))

	inputFile = TFile("pedestalTest_{0}.root".format(d),"READ")
	gStyle.SetFillColor(0)
	can = TCanvas("can","can",500,500)
	can1=TCanvas('can1','can1',1200,400)
	can1.Divide(3,1)
	means=TH1F('mean','mean',20,0,10)
	rmss=TH1F('rms','rms',18,0,6)
	print "plotting histograms..."
	for link  in links : 
		if not link.on : continue
		if link.n is -1: 
			print "---------------------------"
			print 'BAD LINK'
			continue
		print "---------------------------"
		link.Print()
		print "---------------------------"
		h = [ ]
		can.cd()
		for i in range(4):
			temp = inputFile.Get("h{0}".format(4*link.n+i) )
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
			xs.append(4*link.n+i)
			ys.append(temp.GetMean())
			xers.append(0)
			yers.append(temp.GetRMS())
#		can.SaveAs("pedestalTest_{0}_link{1}.eps".format(d,link.n))
		can.SaveAs("pedestalTest_{0}_link{1}.png".format(d,link.n))
#		can.SaveAs("pedestalTest_{0}_link{1}.pdf".format(d,link.n))
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
	can1.Print('ped_{0}.png'.format(d))
