####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: Reads in 100 BXs of SPY data from each active link  #
# and prints out the average and standard deviation.               #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys
import numpy

if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)

#	ts.set_ped()
#	ts.set_fixed_range()
	link_dict = ts.get_links()
	for crate_slot, links in link_dict.iteritems():
		crate, slot = crate_slot
		active_links = [l for l in links if l.on]
		print "\nResults for the uHTR in BE Crate {0}, BE Slot {1}:".format(crate, slot)
		print "The activated links are {0}.".format([l.n for l in active_links])
		for link in active_links:
			print "==== Link {0} ====".format(link.n)
			data = link.get_data_spy()
			print "Read in {0} bunch crossings.".format(len(data[0]))
			for ch in range(4):
				adcs = [d.adc for d in data[ch]]
				print "Channel {0}: ADC_avg = {1:.2f} (sigma = {2:.2f})".format(ch, numpy.mean(adcs), numpy.std(adcs))
