from hcal_teststand.hcal_teststand import *
import hcal_teststand.uhtr
import numpy
import sys
import hcal_teststand.qie
from datetime import date
from ROOT import *

# one big (?) issue with this whole setup, that maybe is 
# solved somehow, is that we want to be able to run tests 
# for individual QIE cards.  If there are multiple QIE 
# cards per uHTR we will also need to figure out which 
# channel of the uHTR connects to which QIE card.  


if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)

	#ts.set_ped_all(6)
	#set_ped(crate_port, 3, 31)
	links = uhtr.get_links(ts,12)
	#for link in links : 
	#        link.Print()

	d = date.fromordinal(730920) # 730920th day after 1. 1. 0001
	print "pedestalTest_{0}.root".format(d.isoformat())
	uhtr.get_histo(ts,12,1000,0,"pedestalTest_{0}.root".format(d.isoformat()))

	inputFile = TFile("pedestalTest_{0}.root".format(d.isoformat()),"READ")

	can = TCanvas("can","can",500,500)

	print "plotting histograms..."
	for link  in links : 
		if not link.on : continue
		print "---------------------------"
		link.Print()
		print "---------------------------"
		h = [ ]
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
		can.SaveAs("pedestalTest_{0}_link{1}.eps".format(d.isoformat(),link.n))
		can.SaveAs("pedestalTest_{0}_link{1}.png".format(d.isoformat(),link.n))
		can.SaveAs("pedestalTest_{0}_link{1}.pdf".format(d.isoformat(),link.n))
