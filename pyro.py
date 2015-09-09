from ROOT import *
from time import sleep

b = [0, 0, 1, 2, 2, 3, 4, 4]

c1 = TCanvas("c1", "Window Title", 500, 500)
histogram = TH1F("Legend", "Title", 16, -0.5, 15.5)
histogram.GetXaxis().CenterTitle(1)
histogram.GetXaxis().SetTitle("x label")
histogram.GetYaxis().CenterTitle(1)
histogram.GetYaxis().SetTitle("y label")
histogram.GetYaxis().SetTitleOffset(1.3)
histogram.SetLineColor(kRed)
histogram.SetFillColor(kBlue)
for x in b:
	histogram.Fill(x)
histogram.Draw()
while True: pass
